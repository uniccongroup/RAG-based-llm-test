# BrightPath Academy FAQ Chatbot (Aria)

A RAG-powered student support chatbot for BrightPath Academy, built with
FastAPI, LangChain, AstraDB, and Google Gemini.

## Live Demo
https://brightpath-ai-fi16.onrender.com

## Architecture
- **Framework**: FastAPI
- **Vector Store**: AstraDB (Datastax)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (local, CPU)
- **LLM**: Google Gemini 2.5 Flash Lite via LangChain
- **Knowledge Base**: 5 BrightPath Academy documents (FAQs, Course Catalogue,
  Student Policies, Onboarding Guide, Contact & Support)

## How it works
1. Student asks a question via POST /api/chat
2. The question is embedded using sentence-transformers
3. AstraDB returns the 5 most semantically similar document chunks
4. Chunks + question are passed to Gemini with a hardened system prompt
5. Gemini returns a grounded answer citing only the knowledge base

## Security
- Input sanitisation blocks known prompt injection patterns
- System prompt hardened against language switching, persona hijacking,
  and source extraction attacks
- Output validator catches accidental system prompt leakage

## Running locally
1. Clone the repo
2. Create a `.env` file with your API keys (see `.env.example`)
3. Run the ingestion notebook once: `brightpath injestion.ipynb`
4. Start the server: `uvicorn app.main:app --reload --port 8000`
5. Open http://localhost:8000

## Environment variables
| Variable | Description |
|---|---|
| GOOGLE_API_KEY | Google AI Studio API key |
| ASTRA_DB_API_ENDPOINT | AstraDB database endpoint |
| ASTRA_DB_APPLICATION_TOKEN | AstraDB application token |
| ASTRA_DB_NAMESPACE | Keyspace name (default: default_keyspace) |
| ASTRA_DB_COLLECTION | Collection name (default: brightpath_rag) |

## Running tests
pip install pytest httpx
pytest tests/ -v

## Tech stack
FastAPI · LangChain · AstraDB · Google Gemini · sentence-transformers ·
HuggingFace · Docker · Render
