# Local Ollama Chatbot

A local-first chatbot project for the Generative AI Training Assessment. The requirements and implementation approach are documented in [SPEC.md](SPEC.md) and [PLAN.md](PLAN.md); [TASKS.md](TASKS.md) tracks implementation progress.

## Prerequisites

- Python 3.11 or later
- Ollama installed and running locally
- At least one chat model downloaded in Ollama

## Setup

From this directory, create and activate a virtual environment, then install the project:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

The default chat model is `mistral`. Pull it with `ollama pull mistral` if it is not installed. You can set `OLLAMA_CHAT_MODEL` in `.env` to another model shown by `ollama list`. Start Ollama if it is not already running. Then launch the UI:

```powershell
python -m streamlit run app.py
```

The app uses the local Ollama endpoint by default. It does not send prompts to a hosted AI provider. The document/RAG dependencies are included for later implementation phases; the current app implements basic chat only.

## Tests

```powershell
python -m pytest
```