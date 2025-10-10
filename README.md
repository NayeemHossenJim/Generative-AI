# 🤖 Generative AI Projects Hub

<div align="center">

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Repo Size](https://img.shields.io/github/repo-size/NayeemHossenJim/Generative-AI?color=orange)](https://github.com/NayeemHossenJim/Generative-AI)

<img src="https://img.shields.io/badge/LangChain-121212?style=for-the-badge&logo=chainlink&logoColor=white"/>
<img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white"/>
<img src="https://img.shields.io/badge/Hugging Face-FFAE33?style=for-the-badge&logo=huggingface&logoColor=black"/>
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white"/>

</div>

A comprehensive collection of Generative AI examples, utilities, and reference implementations using LangChain-compatible models, embeddings, and retrievers. This repository is organized to help you quickly prototype chatbots, embedding pipelines, vector stores, and retrieval-augmented generation (RAG) flows.

## ✨ Why This Repository?

🎯 **Curated Examples**
- Comprehensive collection of GenAI building blocks
- Models, embeddings, retrievers, chains, and runnables
- Production-ready patterns and implementations

🚀 **Quick Iteration**
- Ready-to-run scripts & notebooks
- Clear, documented examples
- Fast prototyping capabilities

🛠️ **Framework Agnostic**
- Lightweight implementation patterns
- Easy to integrate into existing projects
- Flexible and adaptable codebase

## 📚 Table of Contents
- [Highlights](#highlights)
- [Quickstart](#quickstart)
- [Folder Map](#folder-map)
- [Examples](#examples)
- [Development & Testing](#development--testing)
- [Contributing](#contributing)
- [License](#license)

## 🌟 Key Features

### 🤖 Models & Integrations
- LangChain-style implementations for both local and cloud models
- Full support for Hugging Face's local models and model hub
- Integration with OpenAI, Anthropic, and Google AI services
- Local model deployment with Hugging Face Transformers
- Cloud API integrations for production deployments

### 📊 Embeddings & Search
- Sophisticated embedding creation workflows
- Hugging Face Sentence Transformers integration
- OpenAI-compatible embedding models
- Advanced similarity search patterns
- Optimized vector storage solutions

### 🔍 Retriever Strategies
- MMR (Maximal Marginal Relevance)
- Multi-query implementations
- Contextual compression techniques

### 💬 Interactive Chatbots
- YouTube Q&A Chatbot with transcript analysis
- PDF Chatbot with FastAPI integration
- Working Chroma/FAISS store implementations

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.8+
- Windows with PowerShell (for Windows users)
- API keys for various services (optional)

### Installation Steps

1️⃣ **Create a Virtual Environment** (Recommended)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2️⃣ **Install Dependencies**
```powershell
pip install -r requirements.txt
```

3️⃣ **Quick Test**
```powershell
# Run the repository-level smoke test
python "1.Langchain Models\test.py"
```

Notes:
- Some examples require API keys (OpenAI, Anthropic, Google). Export them as environment variables or configure according to each script's README.
- Notebooks are runnable in Jupyter / VS Code.

## Folder Map
Top-level folders and what they contain (quick glance):

- `1.Langchain Models/` — model wrappers and quick tests for LLMs and chat models.
	- `1.LLMS/` — core LLM adapter code
	- `2.ChatModels/` — provider-specific chat model examples
	- `3.EmbeddedModels/` — embedding creation scripts and similarity utilities

- `2.Langchain Prompts/` — prompt templates, prompt UI helpers and generators
- `3.Langchain Structure Output/` — examples and utilities for structured outputs and Pydantic integration
- `4.Langchain Parser Output/` — parsers for string and pydantic outputs
- `5.Langchain Chains/` — chain patterns: simple, sequential, parallel, conditional
- `6.Langchain Runnables/` — runnable utilities and composition helpers
- `7.Langchain Document Loader/` — loader examples (PDF & text)
- `8.Langchain Text Splitters/` — text splitting strategies
- `9.Langchain Vector Database/` — chroma samples and persisted DBs
- `10.Langchain Retrievers/` — notebook demos for retrieval strategies
- `11.Youtube QNA Chatbot/` — notebook demo for building a YouTube-Q&A assistant
- `12.PDF Chatbot/` — FastAPI service and dockerfile for a PDF-based chatbot with a local Chroma DB

Files worth checking:
- `requirements.txt` — Python dependencies
- `LICENSE` — repository license
- `README.md` — this file

## Examples
Small curated examples you can try quickly:

- Run a model test (example):

```powershell
python "1.Langchain Models\test.py"
```

- Start the PDF Chatbot FastAPI server (inside `12.PDF Chatbot/`):

```powershell
cd "12.PDF Chatbot"
pip install -r requirements.txt
python FastAPI.py
```

- Open the Jupyter notebooks for interactive demos (recommended):

```powershell
# from repo root
jupyter notebook
```

## Development & Testing
- Keep code style consistent with the repo conventions. Small helper scripts are plain Python files.
- Add minimal unit tests when you extract reusable logic. There are no centralized tests yet — adding pytest-based tests is a recommended next step.

Quality gates (recommended):
- Build: verify package installs from `requirements.txt`.
- Linting: run flake8/black if you add them to dev requirements.

## Contributing
Contributions are welcome. If you'd like to add examples, fix bugs or improve docs:

1. Fork the repo and create a feature branch.
2. Open a clear PR with a description and a short demo (screenshots or short steps).
3. Keep changes focused and add tests when adding logic.

If you want help onboarding a feature or cleaning up examples, open an issue and tag it with `help wanted`.

## 🔒 Security & API Keys

⚠️ **Important Security Notes:**
- Never commit secrets, API keys, or service account files
- Use environment variables or a secrets manager
- Keep sensitive information out of version control

Example API key setup (PowerShell):
```powershell
$env:OPENAI_API_KEY = "sk-..."
$env:ANTHROPIC_API_KEY = "sk-..."
$env:GOOGLE_API_KEY = "..."
$env:HUGGINGFACE_API_TOKEN = "..."
```

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔜 Coming Soon
- 📝 Detailed CONTRIBUTING.md with templates
- 🧪 Pytest harness for core modules
- 🐳 Docker/Devcontainer setup for reproducible environments

<div align="center">
  
### 🌟 Star this repository if you find it helpful!

[![GitHub stars](https://img.shields.io/github/stars/NayeemHossenJim/Generative-AI.svg?style=social&label=Star)](https://github.com/NayeemHossenJim/Generative-AI)

</div>

Happy Building! 🚀
