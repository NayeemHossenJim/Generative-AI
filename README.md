# Generative-AI

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Repo Size](https://img.shields.io/github/repo-size/NayeemHossenJim/Generative-AI?color=orange)](https://github.com/NayeemHossenJim/Generative-AI)

An opinionated, practical collection of Generative AI examples, utilities and reference implementations using LangChain-compatible models, embeddings and retrievers. This repository is organized to help you quickly prototype chatbots, embedding pipelines, vector stores, and retrieval-augmented generation (RAG) flows.

Why this repo?
- Curated examples across common GenAI building blocks (models, embeddings, retrievers, chains, runnables).
- Ready-to-run scripts & notebooks to help you iterate fast.
- Lightweight, framework-agnostic patterns you can copy into your projects.

## Table of Contents
- [Highlights](#highlights)
- [Quickstart](#quickstart)
- [Folder Map](#folder-map)
- [Examples](#examples)
- [Development & Testing](#development--testing)
- [Contributing](#contributing)
- [License](#license)

## Highlights
- LangChain-style examples for local and cloud models (OpenAI, Anthropic, Google, Hugging Face).
- Embedding creation and similarity search patterns.
- Multiple retriever strategies (MMR, multi-query, contextual compression).
- Sample chatbot notebooks (YouTube Q&A, PDF chatbot) and working Chroma/FAISS stores included.

## Quickstart
Minimal steps to run the examples on Windows (PowerShell). This assumes you have Python 3.8+ installed.

1. Create and activate a virtual environment (optional but recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run a quick smoke test (example script):

```powershell
# example: run the repository-level smoke test if present
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

## Security & API keys
- Do NOT commit secrets, API keys, or service account files to the repository. Use environment variables or a secrets manager.

Example (PowerShell):

```powershell
$env:OPENAI_API_KEY = "sk-..."
```

## License
This project is licensed under the MIT License — see the `LICENSE` file for details.

---

If you'd like, I can also:
- add a small CONTRIBUTING.md with templates,
- add a quick pytest harness for one or two core modules,
- or generate Docker/Devcontainer files for reproducible dev environments.

Happy building!
