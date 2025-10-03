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
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.embeddings import HuggingFaceEmbeddings

# 🔹 Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# 🔹 Streamlit app title
st.title("ChatGroq with Llama3 & HuggingFace Embeddings")

# 🔹 Initialize Groq LLM
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama-3.3-70b-versatile"
)

# 🔹 Prompt template
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

# 🔹 Function to create vector embeddings & save to FAISS + ChromaDB
def vector_embedding():
    if "vectors" not in st.session_state:
        # ✅ HuggingFace Embeddings
        st.session_state.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # ✅ Load PDFs
        st.session_state.loader = PyPDFDirectoryLoader("./PDF")
        st.session_state.docs = st.session_state.loader.load()

        # ✅ Split documents
        st.session_state.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        st.session_state.final_documents = st.session_state.text_splitter.split_documents(
            st.session_state.docs[:20]
        )  # limit to first 20 docs

        # ✅ Create FAISS vector store (in memory)
        st.session_state.vectors = FAISS.from_documents(
            st.session_state.final_documents,
            st.session_state.embeddings
        )

        # 🔹 Save FAISS to disk (so you can reload later)
        FAISS.save_local(st.session_state.vectors, "faiss_index")

        # ✅ Create ChromaDB vector store
        st.session_state.chroma_db = Chroma.from_documents(
            st.session_state.final_documents,
            st.session_state.embeddings,
            persist_directory="./chroma_db"
        )
        st.session_state.chroma_db.persist()

        st.success("✅ Vector Store saved to FAISS & ChromaDB")

# 🔹 Button to build vector DB
if st.button("First Press the button to build Vector DB"):
    vector_embedding()
    st.write("✅ Vector Store DB is ready")

# 🔹 Input box
prompt1 = st.text_input("Enter your question from the documents")

# 🔹 Handle user query
if prompt1:
    if "vectors" not in st.session_state:
        st.warning("⚠️ Please build embeddings first by clicking the button above.")
    else:
        document_chain = create_stuff_documents_chain(llm, prompt)
        retriever = st.session_state.vectors.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        start = time.process_time()
        response = retrieval_chain.invoke({'input': prompt1})
        end = time.process_time()

        st.write("### 📌 Answer:")
        st.write(response['answer'])
        st.caption(f"Response time: {round(end - start, 2)} seconds")

        # 🔹 Show retrieved docs
        with st.expander("📑 Document Chunks Used"):
            for i, doc in enumerate(response["context"]):
                st.write(doc.page_content)
                st.write("--------------------------------")

# docker run -p 8501:8501 rag-based-chatgroq