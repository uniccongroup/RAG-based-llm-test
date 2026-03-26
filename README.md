---
title: Academy X AI Chatbot
emoji: 🤖
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Academy X RAG Chatbot

A production-ready **RAG (Retrieval-Augmented Generation)** FAQ chatbot backend built with FastAPI for the UNICCON AI Engineer assessment. It powers an intelligent assistant for **Academy X**, a tech training hub, by grounding LLM responses in a proprietary knowledge base.

**Live UI**: `/ui` · **Swagger Docs**: `/docs` · **Branch**: `john-eze`

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI 0.104+ (async) |
| LLM | Qwen/Qwen2.5-7B-Instruct via HuggingFace InferenceClient |
| Vector Search | TF-IDF + Cosine Similarity (scikit-learn) |
| Server | Uvicorn |
| Deployment | HuggingFace Spaces (Docker) |

---

## Project Structure

```
uniccon/
├── app/
│   ├── main.py                 # FastAPI app, routes, static files
│   ├── api/
│   │   ├── router.py           # API router
│   │   └── chat.py             # Chat, upload, health endpoints
│   ├── core/
│   │   ├── config.py           # Settings (pydantic-settings + .env)
│   │   └── logger.py           # Logging setup
│   ├── models/
│   │   └── schemas.py          # Pydantic request/response models
│   ├── services/
│   │   ├── rag_service.py      # RAG orchestration + greeting handling
│   │   ├── vector_store.py     # TF-IDF vector store
│   │   ├── chunking.py         # Text chunking
│   │   └── llm_service.py      # LLM provider abstraction
│   └── static/
│       └── index.html          # Chat UI
├── data/
│   ├── faq.txt                 # Academy X FAQs
│   ├── courses.txt             # Course catalogue
│   ├── policies.txt            # Student policies
│   ├── support.txt             # Support information
│   └── index.pkl               # Pre-built TF-IDF index (29 chunks)
├── Dockerfile                  # HuggingFace Spaces compatible (port 7860)
├── render.yaml                 # Render.com deployment config
├── setup_kb.py                 # Build the knowledge base index
├── run.py                      # Entry point (reads PORT env var)
├── requirements.txt
└── .env                        # Local environment variables
```

---

## Local Setup

### 1. Prerequisites
- Python 3.8+
- A [HuggingFace API token](https://huggingface.co/settings/tokens)

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
copy .env.example .env
```
Edit `.env`:
```bash
LLM_PROVIDER=huggingface
HF_MODEL_NAME=Qwen/Qwen2.5-7B-Instruct
HF_API_TOKEN=hf_your_token_here
SIMILARITY_THRESHOLD=0.05
DEBUG=False
```

### 4. Build the knowledge base
```bash
python setup_kb.py
```

### 5. Run
```bash
python run.py
```

App starts at `http://localhost:8000`  
- Chat UI → `http://localhost:8000/ui`  
- Swagger → `http://localhost:8000/docs`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Service health check |
| `POST` | `/api/chat` | Ask a question (RAG pipeline) |
| `POST` | `/api/upload-documents` | Upload `.txt` files to re-index |
| `GET` | `/api/index-status` | Check knowledge base index status |

### Example — Chat
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What courses does Academy X offer?"}'
```
```json
{
  "query": "What courses does Academy X offer?",
  "answer": "Academy X offers tracks in Software Development, Data Science & AI, Cybersecurity, Cloud & DevOps, UI/UX Design, and Product Management...",
  "sources": ["..."],
  "confidence": 0.72
}
```

---

## Deployment — HuggingFace Spaces

The repo is pre-configured for HuggingFace Spaces (Docker SDK, port 7860).

```bash
# Add HF Space as a remote
git remote add space https://huggingface.co/spaces/YOUR_HF_USERNAME/academyx-chatbot

# Push
git push space john-eze:main
```

Then in **Space Settings → Secrets**, add:
- `HF_API_TOKEN` — your HuggingFace token
- `DEBUG` — `False`

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `"Vector store is empty"` | Run `python setup_kb.py` |
| `"No module named 'fastapi'"` | Run `pip install -r requirements.txt` |
| No answers returned | Lower `SIMILARITY_THRESHOLD` in `.env` (default: `0.05`) |
| LLM errors | Check `HF_API_TOKEN` is valid and `HF_MODEL_NAME` is correct |

---

## Submission

> **Repository**: hosted on the UNICCON GitHub  
> **Branch**: `john-eze`  
> **Note**: This is an individual task — collaborations may lead to disqualification.



