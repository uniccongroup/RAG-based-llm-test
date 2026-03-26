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


A production-ready **Retrieval-Augmented Generation (RAG)** FAQ chatbot backend built with **FastAPI**, deployed on HuggingFace Spaces. It powers an intelligent assistant for **Academy X** — a tech training hub — by grounding every LLM response in a proprietary knowledge base of courses, policies, FAQs, and support content.

---

## 🔗 Live Links

| | URL |
|---|---|
| 💬 **Chat UI** | [johneze-academyx-chatbot.hf.space](https://johneze-academyx-chatbot.hf.space) |
| 📖 **Swagger / API Docs** | [johneze-academyx-chatbot.hf.space/docs](https://johneze-academyx-chatbot.hf.space/docs) |
| 🤗 **HuggingFace Space** | [huggingface.co/spaces/johneze/academyx-chatbot](https://huggingface.co/spaces/johneze/academyx-chatbot) |
| 🎙️ **Ava — Voice & Chat Agent** | [jotform.com/agent/019d2989fc0972ac8e1c52ef9d0d3770d736](https://www.jotform.com/agent/019d2989fc0972ac8e1c52ef9d0d3770d736) |

---

## 🧠 How It Works

```
User Query
    │
    ▼
TF-IDF Vector Search  ──►  Top-K Relevant Chunks (from data/*.txt)
    │
    ▼
Prompt Construction  ──►  [System Prompt + Context + User Query]
    │
    ▼
Qwen/Qwen2.5-7B-Instruct (HuggingFace InferenceClient)
    │
    ▼
Synthesised Answer  ──►  Returned via /api/chat
```

**Key design decisions:**
- **TF-IDF over FAISS** — PyTorch/sentence-transformers have DLL incompatibility on Python 3.14; TF-IDF (scikit-learn) is pure Python and equally effective at this scale
- **Direct InferenceClient** — LangChain's `HuggingFaceEndpoint` has a `StopIteration` bug on Python 3.14; bypassed entirely with `huggingface_hub.InferenceClient.chat_completion()`
- **Greeting detection** — common greetings bypass the RAG pipeline for instant, warm responses
- **Prompt engineering** — LLM is instructed to synthesise answers in its own words, never copy context verbatim, and never use traditional academic language

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI 0.104+ (async) |
| LLM | `Qwen/Qwen2.5-7B-Instruct` via HuggingFace InferenceClient |
| Vector Store | TF-IDF + Cosine Similarity (scikit-learn) |
| Server | Uvicorn |
| Deployment | HuggingFace Spaces (Docker, port 7860) |
| Config | pydantic-settings + `.env` |

---

## 📁 Project Structure

```
├── app/
│   ├── main.py                 # FastAPI app — routes, CORS, static files
│   ├── api/
│   │   ├── router.py           # API router
│   │   └── chat.py             # Endpoints: /chat, /upload-documents, /health, /index-status
│   ├── core/
│   │   ├── config.py           # All settings via pydantic-settings + .env
│   │   └── logger.py           # Logging setup
│   ├── models/
│   │   └── schemas.py          # Pydantic request/response models
│   ├── services/
│   │   ├── rag_service.py      # RAG orchestration + greeting detection
│   │   ├── vector_store.py     # TF-IDF backend (FAISS fallback ready)
│   │   ├── chunking.py         # Text chunking (500 chars, 50 overlap)
│   │   └── llm_service.py      # LLM abstraction (HuggingFace / OpenAI / Cohere / Mock)
│   └── static/
│       └── index.html          # Browser chat UI
├── data/
│   ├── faq.txt                 # Enrollment & admissions FAQs
│   ├── courses.txt             # Course catalogue & descriptions
│   ├── policies.txt            # Student & refund policies
│   └── support.txt             # Technical support information
├── Dockerfile                  # HuggingFace Spaces compatible (port 7860)
├── render.yaml                 # Render.com deployment config
├── setup_kb.py                 # Builds and saves TF-IDF index from data/*.txt
├── run.py                      # Entry point — reads PORT env var for cloud compatibility
├── requirements.txt
└── .env.example                # Environment variables template
```

---

## ⚡ Local Setup

### Prerequisites
- Python 3.8+
- A [HuggingFace API token](https://huggingface.co/settings/tokens) (free)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
copy .env.example .env
# Edit .env — set HF_API_TOKEN at minimum

# 3. Build the knowledge base index
python setup_kb.py

# 4. Run
python run.py
```

App available at `http://localhost:8000`  
Chat UI → `http://localhost:8000/ui`  
Swagger → `http://localhost:8000/docs`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Service health check |
| `POST` | `/api/chat` | Ask a question — full RAG pipeline |
| `POST` | `/api/upload-documents` | Upload `.txt` files to re-index |
| `GET` | `/api/index-status` | Check knowledge base index status |

```bash
# Example
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What courses does Academy X offer?"}'
```

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `HF_API_TOKEN` | ✅ | HuggingFace API token |
| `LLM_PROVIDER` | No | `huggingface` (default), `openai`, `cohere` |
| `HF_MODEL_NAME` | No | Default: `Qwen/Qwen2.5-7B-Instruct` |
| `SIMILARITY_THRESHOLD` | No | Default: `0.05` |
| `TOP_K_RETRIEVAL` | No | Default: `3` |
| `DEBUG` | No | Default: `False` |


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



