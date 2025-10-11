# 🤖 Advanced PDF Chatbot

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Latest-2496ED.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A powerful and intelligent chatbot that can understand and answer questions about your PDF documents using state-of-the-art language models and vector databases.

![Chatbot Demo](https://img.icons8.com/clouds/100/pdf.png)

## ✨ Features

- 📄 Upload multiple PDF documents
- 🔍 Advanced document processing with chunking
- 🧠 Powered by Llama 3 (70B parameter model)
- 💾 Dual vector storage (FAISS & ChromaDB)
- 🎯 Precise answer retrieval
- 🎨 Beautiful Streamlit UI
- 🐳 Docker support for easy deployment

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Language Model**: Llama 3.3 70B (via Groq)
- **Embeddings**: HuggingFace (sentence-transformers)
- **Vector Stores**: 
  - FAISS (Facebook AI Similarity Search)
  - ChromaDB
- **Document Processing**: LangChain
- **Containerization**: Docker

## 🚀 Quick Start with Docker

### Pull the Image

```bash
docker pull jimaifsd/rag-based-chatbot:latest
```

### Run the Container

```bash
docker run -p 8501:8501 jimaifsd/rag-based-chatbot:latest
```

Then open your browser and navigate to [http://localhost:8501](http://localhost:8501)

## 🛠️ Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Chatbot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # On Windows PowerShell:
   venv\Scripts\Activate.ps1
   # On cmd.exe: venv\Scripts\activate.bat
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create a .env file and add your GROQ_API_KEY
   echo GROQ_API_KEY=your_api_key_here > .env
   ```

5. **Run the FastAPI server with built-in UI**
   ```powershell
   python -m uvicorn FastAPI:app --app-dir "12.PDF Chatbot" --reload --port 8000
   ```

6. **Open the app**
   - Go to http://127.0.0.1:8000/ to use the Messenger/WhatsApp-style web UI served by FastAPI.

## 🐳 Docker Development

### Build the Image

```bash
docker build -t pdf-chatbot .
```

### Run in Development Mode

```bash
docker run -p 8501:8501 -v $(pwd):/app pdf-chatbot
```

### Environment Variables in Docker

```bash
docker run -p 8501:8501 --env-file .env pdf-chatbot
```

## 📖 How to Use

1. **Upload PDFs**
   - Click the file upload button
   - Select one or more PDF files
   - Wait for the upload to complete

2. **Build Vector Database**
   - Click "Build Vector DB" button
   - Wait for processing to complete
   - Status will show when ready

3. **Ask Questions**
   - Type your question in the input box
   - Get AI-powered responses
   - View source chunks for transparency

## 🔧 Configuration

The application can be configured through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| GROQ_API_KEY | API key for Groq | Required |
| CHUNK_SIZE | Document chunk size | 1000 |
| CHUNK_OVERLAP | Chunk overlap size | 200 |

## 📈 Performance

- **Response Time**: ~2-5 seconds
- **Memory Usage**: ~500MB-1GB
- **Storage**: Depends on PDF size

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Llama 3 model by Meta AI
- Streamlit for the amazing UI framework
- HuggingFace for embeddings
- FAISS and ChromaDB for vector storage

---
Created by [Jim](https://github.com/NayeemHossenJim)