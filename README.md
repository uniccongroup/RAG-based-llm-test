# Academy X RAG Chatbot


A production-ready **Retrieval-Augmented Generation (RAG)** FAQ chatbot backend built with **FastAPI**, deployed on **Render.com**. It powers an intelligent assistant for **Academy X** — a tech training hub — by grounding every LLM response in a proprietary knowledge base of courses, policies, FAQs, and support content.

---

## 🔗 Live Links

| | URL |
|---|---|
| 💬 **Chat UI** | [academyx-rag-chatbot.onrender.com](https://academyx-rag-chatbot.onrender.com) |
| 📖 **Swagger / API Docs** | [academyx-rag-chatbot.onrender.com/docs](https://academyx-rag-chatbot.onrender.com/docs) |
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
| Deployment | Render.com (Python web service) |
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
├── Dockerfile                  # Docker image (local / alternative deployments)
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

## Deployment — Render.com

The repo is pre-configured for Render.com via `render.yaml`.

1. Push this repo to GitHub (branch `john-eze`)
2. Go to [render.com](https://render.com) → **New → Web Service**
3. Connect your GitHub repo and select the `john-eze` branch
4. Render auto-detects `render.yaml` — no manual config needed
5. In **Environment → Secret Files / Env Vars**, add:
   - `HF_API_TOKEN` — your HuggingFace token
   - `LLM_PROVIDER` — `huggingface`
   - `DEBUG` — `False`
6. Click **Deploy** — the live URL will be `https://academyx-rag-chatbot.onrender.com`

> **Note:** The free tier spins down after 15 min of inactivity; the first request after spin-down may take ~30 s.

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

> **Repository**: [github.com/johnemekaeze/academyx-rag-chatbot](https://github.com/johnemekaeze/academyx-rag-chatbot)  
> **Branch**: `main`



