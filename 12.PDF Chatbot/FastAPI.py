import os
import tempfile
import shutil
import time
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from dotenv import load_dotenv


load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = FastAPI(title='PDF Chatbot API')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])


# Serve static UI
if os.path.isdir(STATIC_DIR):
    app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')


@app.get('/')
def index():
    index_path = os.path.join(STATIC_DIR, 'index.html')
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail='UI not found. Ensure static assets are present.')
    return FileResponse(index_path)

# In-memory store for uploaded files and vectors
STATE = {
    'upload_dir': None,
    'pdf_paths': [],
    'vectors': None,
}


class QueryRequest(BaseModel):
    question: str


# Prompt template string (we'll instantiate the chat prompt lazily)
PROMPT_TMPL = (
    """
Answer the questions based on the provided context only.
Please provide the most accurate response based on the question.
<context>
{context}
<context>
Question: {input}
"""
)


@app.post('/upload')
async def upload(file: UploadFile = File(...)):
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail='Only PDF files are supported')

    if STATE['upload_dir'] is None:
        STATE['upload_dir'] = tempfile.mkdtemp(prefix='pdf_upload_')

    path = os.path.join(STATE['upload_dir'], file.filename)
    with open(path, 'wb') as f:
        shutil.copyfileobj(file.file, f)
    STATE['pdf_paths'].append(path)
    return {'ok': True, 'path': path}


@app.post('/build')
def build():
    if not STATE['pdf_paths']:
        raise HTTPException(status_code=400, detail='No PDF files uploaded. Please upload PDFs first.')

    # Lazy imports to avoid heavy deps at import time
    try:
        from langchain_community.document_loaders import PyPDFLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS, Chroma
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Missing or incompatible dependencies for build: {e}")

    # Load and split documents
    docs = []
    for path in STATE['pdf_paths']:
        loader = PyPDFLoader(path)
        docs.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    final_documents = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    vectors = FAISS.from_documents(final_documents, embeddings)

    # Save local
    FAISS.save_local(vectors, os.path.join(BASE_DIR, 'faiss_index'))

    chroma_db = Chroma.from_documents(final_documents, embeddings, persist_directory=os.path.join(BASE_DIR, 'chroma_db'))
    chroma_db.persist()

    STATE['vectors'] = vectors
    return {'ok': True, 'message': 'Congratulations! Vector database built successfully.'}


@app.post('/query')
def query(q: QueryRequest):
    if STATE['vectors'] is None:
        raise HTTPException(status_code=400, detail='Dear user, no vector database found. Please upload PDFs and build the vector DB first.')
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail='GROQ_API_KEY is not set. Please add it to a .env file or environment variables.')
    # Lazy imports
    try:
        from langchain_groq import ChatGroq
        from langchain.chains.combine_documents import create_stuff_documents_chain
        from langchain_core.prompts import ChatPromptTemplate
        from langchain.chains import create_retrieval_chain
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Missing or incompatible dependencies for query: {e}")

    retriever = STATE['vectors'].as_retriever()

    try:
        pre_docs = retriever.get_relevant_documents(q.question)
    except Exception:
        pre_docs = retriever(q.question) if callable(retriever) else []

    if not pre_docs:
        raise HTTPException(status_code=404, detail='No relevant documents found in the vector database for the given question. Please upload PDFs and rebuild the vector DB, or try a different query.')
    llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name='llama-3.3-70b-versatile')
    prompt = ChatPromptTemplate.from_template(PROMPT_TMPL)
    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    start = time.process_time()
    resp = retrieval_chain.invoke({'input': q.question})
    end = time.process_time()

    # Serialize context documents (avoid JSON serialization errors)
    ctx = resp.get('context', [])
    try:
        serialized_ctx = [
            {
                'page_content': getattr(d, 'page_content', str(d)),
                'metadata': getattr(d, 'metadata', {}),
            }
            for d in (ctx or [])
        ]
    except Exception:
        serialized_ctx = []

    return {
        'answer': resp.get('answer'),
        'context': serialized_ctx,
        'time': round(end - start, 2),
    }


@app.get('/health')
def health():
    return {'status': 'ok', 'uploaded_files': len(STATE['pdf_paths'])}
