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


# -------------------------------------------------------------------------
# STATE
# -------------------------------------------------------------------------
STATE = {
    'upload_dir': None,
    'pdf_paths': [],
    'vectors': None,
}


class QueryRequest(BaseModel):
    question: str


# -------------------------------------------------------------------------
# Modern Prompt Template (compatible with Runnable workflow)
# -------------------------------------------------------------------------
PROMPT_TMPL = """
You are Jim, a knowledgeable and professional assistant. Your role is to provide clear, concise, and accurate answers. Respond in a helpful, professional tone, staying in character as Jim.

Use ONLY the information provided in the <context> section. Do NOT provide any information outside of it.

<context>
{context}
</context>

Question: {input}

Answer as Jim. Occasionally, sign your answers with “—Jim” for emphasis, but it’s not required on every response.
"""



# -------------------------------------------------------------------------
# UPLOAD PDF
# -------------------------------------------------------------------------
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


# -------------------------------------------------------------------------
# BUILD VECTOR DB
# -------------------------------------------------------------------------
@app.post('/build')
def build():
    if not STATE['pdf_paths']:
        raise HTTPException(status_code=400, detail='No PDF files uploaded. Please upload PDFs first.')

    try:
        from langchain_community.document_loaders import PyPDFLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS, Chroma
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Missing or incompatible dependencies: {e}")

    # Load all PDF pages
    docs = []
    for path in STATE['pdf_paths']:
        loader = PyPDFLoader(path)
        loaded = loader.load()
        # filter out empty pages
        loaded = [d for d in loaded if d.page_content.strip()]
        docs.extend(loaded)

    if not docs:
        raise HTTPException(status_code=400, detail="All PDF pages were empty. Cannot build vectors.")

    # Chunking
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    # Remove empty chunks
    chunks = [c for c in chunks if c.page_content.strip()]
    if not chunks:
        raise HTTPException(status_code=400, detail="All PDF chunks were empty after splitting.")

    # Correct modern embeddings import
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Build FAISS safely
    vectors = FAISS.from_documents(chunks, embeddings)

    # Persist indexes
    FAISS.save_local(vectors, os.path.join(BASE_DIR, 'faiss_index'))

    chroma = Chroma.from_documents(
        chunks, embeddings,
        persist_directory=os.path.join(BASE_DIR, 'chroma_db')
    )
    chroma.persist()

    STATE['vectors'] = vectors
    return {'ok': True, 'message': 'Vector DB built successfully with modern LangChain.'}

# -------------------------------------------------------------------------
# QUERY (Modern LangChain Runnables RAG)
# -------------------------------------------------------------------------
@app.post('/query')
def query(q: QueryRequest):
    if STATE['vectors'] is None:
        raise HTTPException(status_code=400, detail='No vector database found. Please upload PDFs and build first.')

    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail='GROQ_API_KEY is not set.')

    try:
        from langchain_groq import ChatGroq
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.runnables import RunnablePassthrough, RunnableParallel
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Missing or incompatible dependencies: {e}")

    retriever = STATE['vectors'].as_retriever()

    # LLM
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name='llama-3.3-70b-versatile'
    )

    # Prompt
    prompt = ChatPromptTemplate.from_template(PROMPT_TMPL)

    # New Runnable RAG pipeline
    rag_chain = (
        {
            "context": retriever,
            "input": RunnablePassthrough(),
        }
        | prompt
        | llm
    )

    # Also return retrieved docs (optional)
    rag_with_docs = RunnableParallel(
        answer=rag_chain,
        docs=retriever
    )

    start = time.time()
    result = rag_with_docs.invoke(q.question)
    end = time.time()

    # Serialize context safely
    serialized_docs = [
        {
            "page_content": getattr(d, "page_content", ""),
            "metadata": getattr(d, "metadata", {}),
        }
        for d in result["docs"]
    ]

    return {
        "answer": result["answer"].content,
        "context": serialized_docs,
        "time": round(end - start, 2),
    }


# -------------------------------------------------------------------------
# HEALTH
# -------------------------------------------------------------------------
@app.get('/health')
def health():
    return {'status': 'ok', 'uploaded_files': len(STATE['pdf_paths'])}
