import os
import tempfile
import shutil
import time
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dotenv import load_dotenv

# LangChain imports (same as original app.py)
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS, Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings


load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

app = FastAPI(title='PDF Chatbot API')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

# In-memory store for uploaded files and vectors
STATE = {
    'upload_dir': None,
    'pdf_paths': [],
    'vectors': None,
}


class QueryRequest(BaseModel):
    question: str


PROMPT = ChatPromptTemplate.from_template("""
Answer the questions based on the provided context only.
Please provide the most accurate response based on the question.
<context>
{context}
<context>
Question: {input}
""")


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
    FAISS.save_local(vectors, 'faiss_index')

    chroma_db = Chroma.from_documents(final_documents, embeddings, persist_directory='./chroma_db')
    chroma_db.persist()

    STATE['vectors'] = vectors
    return {'ok': True, 'message': 'Congratulations! Vector database built successfully.'}


@app.post('/query')
def query(q: QueryRequest):
    if STATE['vectors'] is None:
        raise HTTPException(status_code=400, detail='Dear user, no vector database found. Please upload PDFs and build the vector DB first.')

    retriever = STATE['vectors'].as_retriever()
    llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name='llama-3.3-70b-versatile')
    document_chain = create_stuff_documents_chain(llm, PROMPT)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    start = time.process_time()
    resp = retrieval_chain.invoke({'input': q.question})
    end = time.process_time()

    # respond with answer and context
    return {'answer': resp.get('answer'), 'context': resp.get('context', []), 'time': round(end - start, 2)}


@app.get('/health')
def health():
    return {'status': 'ok', 'uploaded_files': len(STATE['pdf_paths'])}
