import streamlit as st
import os
import time
from dotenv import load_dotenv
import tempfile

from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS, Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings

# 🔹 Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Page Configuration
st.set_page_config(
    page_title="PDF Chatbot with Llama3",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
    <style>
        .main {
            background-color: #f4f6f8;
            padding: 2rem;
        }
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            height: 3em;
            width: 100%;
            font-size: 16px;
        }
        .stTextInput > div > div > input {
            font-size: 16px;
        }
        .response-box {
            background-color: black;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .pdf-upload {
            background-color: #e8f0fe;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# App Header
st.markdown("<h1 style='text-align: center; color: #2E86C1;'>📄 Ask Your PDF Anything</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Powered by Llama3, HuggingFace & FAISS | CHROMADB </p>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar Info
with st.sidebar:
    st.image("https://img.icons8.com/clouds/100/pdf.png", width=100)
    st.markdown("### 🔧 Instructions")
    st.markdown("""
        1. Upload one or more PDF files  
        2. Click **Build Vector DB**  
        3. Ask any question about the uploaded PDFs  
    """)
    st.markdown("Made with 🤖 by Jim")

# PDF Upload Section
st.markdown("### 📂 Upload Your PDF Files")
with st.container():
    uploaded_files = st.file_uploader(
        "Upload one or more PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        help="Only .pdf files are supported",
    )

# Prompt Template
prompt = ChatPromptTemplate.from_template("""
Answer the questions based on the provided context only.
Please provide the most accurate response based on the question.
<context>
{context}
<context>
Question: {input}
""")

# Build Vector DB
def build_vector_db(uploaded_files):
    if not uploaded_files:
        st.warning("⚠️ Please upload at least one PDF.")
        return

    with st.spinner("🔄 Processing PDFs and building vector database..."):
        temp_dir = tempfile.mkdtemp()
        pdf_paths = []

        for file in uploaded_files:
            temp_path = os.path.join(temp_dir, file.name)
            with open(temp_path, "wb") as f:
                f.write(file.read())
            pdf_paths.append(temp_path)

        # Load and split documents
        docs = []
        for path in pdf_paths:
            loader = PyPDFLoader(path)
            docs.extend(loader.load())

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        final_documents = text_splitter.split_documents(docs)

        # Generate embeddings
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectors = FAISS.from_documents(final_documents, embeddings)

        # Optional: Save locally
        FAISS.save_local(vectors, "faiss_index")

        # Optional: Save with Chroma
        chroma_db = Chroma.from_documents(
            final_documents,
            embeddings,
            persist_directory="./chroma_db"
        )
        chroma_db.persist()

        st.session_state.vectors = vectors
        st.session_state.docs_ready = True

        st.success("✅ Vector DB created from uploaded PDFs!")

# Build Vector Button
if st.button("🚀 Build Vector DB"):
    build_vector_db(uploaded_files)

# Text Input for Questions
st.markdown("### 💬 Ask a Question")
user_input = st.text_input("Type your question here...")

# Handle Q&A
if user_input:
    if "vectors" not in st.session_state:
        st.warning("⚠️ Please upload PDFs and build the vector store first.")
    else:
        retriever = st.session_state.vectors.as_retriever()
        llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama-3.3-70b-versatile"
        )

        document_chain = create_stuff_documents_chain(llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        with st.spinner("🤖 Thinking..."):
            start = time.process_time()
            response = retrieval_chain.invoke({'input': user_input})
            end = time.process_time()

        st.markdown("### 📌 Answer")
        st.markdown(f"<div class='response-box'>{response['answer']}</div>", unsafe_allow_html=True)
        st.caption(f"⏱️ Response Time: {round(end - start, 2)} seconds")

        # Show source chunks
        with st.expander("📑 Source Document Chunks"):
            for i, doc in enumerate(response["context"]):
                st.markdown(f"**Chunk {i+1}:**")
                st.markdown(f"> {doc.page_content}")
                st.write("---")
