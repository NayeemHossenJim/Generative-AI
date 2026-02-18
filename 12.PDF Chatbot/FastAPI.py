import os
import time
import shutil
import tempfile
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, HTTPException

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

FAISS_DIR = os.path.join(BASE_DIR, "faiss_openai_1536")

app = FastAPI(title="Persistent PDF RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# -------------------- STATE --------------------
STATE = {
    "upload_dir": None,
    "pdf_paths": [],
    "vectors": None,
}

class QueryRequest(BaseModel):
    question: str

PROMPT_TMPL = """
Use ONLY the information inside <context>

<context>
{context}
</context>

Question: {input}
"""

# -------------------- AUTO LOAD EXISTING KNOWLEDGE --------------------
@app.on_event("startup")
def load_existing_index():

    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS

    if os.path.exists(FAISS_DIR):

        embeddings = OpenAIEmbeddings(
            api_key=OPENAI_API_KEY,
            model="text-embedding-3-small"
        )

        STATE["vectors"] = FAISS.load_local(
            FAISS_DIR,
            embeddings,
            allow_dangerous_deserialization=True
        )

        print("✅ Knowledge Base Loaded Automatically")

# -------------------- UPLOAD --------------------
@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="PDF only")

    if STATE["upload_dir"] is None:
        STATE["upload_dir"] = tempfile.mkdtemp(prefix="pdf_upload_")

    path = os.path.join(STATE["upload_dir"], file.filename)

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    STATE["pdf_paths"].append(path)

    return {"ok": True}

# -------------------- BUILD ONCE --------------------
@app.post("/build")
def build():

    if not STATE["pdf_paths"]:
        raise HTTPException(status_code=400, detail="Upload PDFs first")

    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS

    # DELETE OLD INDEX ONLY WHEN BUILDING NEW ONE
    if os.path.exists(FAISS_DIR):
        shutil.rmtree(FAISS_DIR)

    docs = []

    for path in STATE["pdf_paths"]:
        loader = PyPDFLoader(path)
        docs.extend([d for d in loader.load() if d.page_content.strip()])

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(
        api_key=OPENAI_API_KEY,
        model="text-embedding-3-small"
    )

    vectors = FAISS.from_documents(chunks, embeddings)

    vectors.save_local(FAISS_DIR)

    STATE["vectors"] = vectors

    return {"ok": True, "message": "Knowledge Base Built Successfully"}

# -------------------- QUERY FOREVER --------------------
@app.post("/query")
def query(q: QueryRequest):

    if STATE["vectors"] is None:
        raise HTTPException(
            status_code=400,
            detail="Knowledge not built yet"
        )

    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnablePassthrough

    retriever = STATE["vectors"].as_retriever(
        search_kwargs={"k": 4}
    )

    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model="gpt-4o-mini",
        temperature=0
    )

    prompt = ChatPromptTemplate.from_template(PROMPT_TMPL)

    rag_chain = (
        {
            "context": retriever,
            "input": RunnablePassthrough(),
        }
        | prompt
        | llm
    )

    start = time.time()
    result = rag_chain.invoke(q.question)
    end = time.time()

    return {
        "answer": result.content,
        "time": round(end - start, 2)
    }

# -------------------- HEALTH --------------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "knowledge_loaded": STATE["vectors"] is not None
    }
