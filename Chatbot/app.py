import streamlit as st
import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS, Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings

import tempfile

# 🔹 Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

st.title("📄 Ask Questions from Your PDF using Llama3 + HuggingFace")

# 🔹 Upload PDF(s)
uploaded_files = st.file_uploader("📂 Upload PDF files", type=["pdf"], accept_multiple_files=True)

# 🔹 Initialize LLM
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama-3.3-70b-versatile"
)

# 🔹 Prompt Template
prompt = ChatPromptTemplate.from_template(
    """
    Answer the questions based on the provided context only.
    Please provide the most accurate response based on the question.
    <context>
    {context}
    <context>
    Question: {input}
    """
)

# 🔹 Create Vector Embedding from Uploaded PDFs
def process_uploaded_pdfs(uploaded_files):
    if not uploaded_files:
        st.warning("⚠️ Please upload at least one PDF.")
        return

    if "vectors" not in st.session_state:
        # Save PDFs to temp files
        temp_dir = tempfile.mkdtemp()
        pdf_paths = []
        for file in uploaded_files:
            temp_path = os.path.join(temp_dir, file.name)
            with open(temp_path, "wb") as f:
                f.write(file.read())
            pdf_paths.append(temp_path)

        # Load PDFs
        docs = []
        for path in pdf_paths:
            loader = PyPDFLoader(path)
            docs.extend(loader.load())

        # Split Documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        final_documents = text_splitter.split_documents(docs)

        # Embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Create FAISS Vector Store
        vectors = FAISS.from_documents(final_documents, embeddings)
        st.session_state.vectors = vectors

        # Optional: Save to disk
        FAISS.save_local(vectors, "faiss_index")

        # (Optional) Chroma DB
        chroma_db = Chroma.from_documents(
            final_documents,
            embeddings,
            persist_directory="./chroma_db"
        )
        chroma_db.persist()

        st.success("✅ Vector store created from uploaded PDFs!")

# 🔹 Button to Process PDFs
if st.button("🔍 Build Vector DB from Uploaded PDFs"):
    process_uploaded_pdfs(uploaded_files)

# 🔹 Question Input
user_query = st.text_input("💬 Ask a question from your documents")

# 🔹 Answer Query
if user_query:
    if "vectors" not in st.session_state:
        st.warning("⚠️ Please upload PDFs and build the vector store first.")
    else:
        document_chain = create_stuff_documents_chain(llm, prompt)
        retriever = st.session_state.vectors.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        start = time.process_time()
        response = retrieval_chain.invoke({'input': user_query})
        end = time.process_time()

        st.write("### 📌 Answer:")
        st.write(response['answer'])
        st.caption(f"⏱️ Response time: {round(end - start, 2)} seconds")

        with st.expander("📑 Document Chunks Used"):
            for i, doc in enumerate(response["context"]):
                st.write(doc.page_content)
                st.write("--------------------------------")