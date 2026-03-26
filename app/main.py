"""Main FastAPI application."""
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.api.router import router
from app.core.config import settings
from app.core.logger import logger

# Configure logging
logging.basicConfig(level=settings.log_level)

STATIC_DIR = Path(__file__).parent / "static"

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="""
## Academy X RAG-based FAQ Chatbot API

This API powers an intelligent FAQ assistant for **Academy X**, a tech training hub.
It uses a **Retrieval-Augmented Generation (RAG)** pipeline to answer questions by searching
a proprietary knowledge base and generating contextual responses via a large language model.

---

### 🚀 Quick Start

1. **Check the service is healthy** — `GET /api/health`
2. **Ask a question** — `POST /api/chat` with `{"query": "What courses do you offer?"}`
3. **Check index status** — `GET /api/index-status`
4. **Upload new documents** — `POST /api/upload-documents` with `.txt` files

---

### 🏗️ Architecture

```
User Query → TF-IDF Retrieval → Top-K Context Chunks → Qwen2.5-7B LLM → Answer
```

- **Vector Store**: TF-IDF + Cosine Similarity (scikit-learn)
- **LLM**: `Qwen/Qwen2.5-7B-Instruct` via HuggingFace InferenceClient
- **Chunking**: 500-character chunks with 50-character overlap
- **Knowledge Base**: Pre-indexed from `data/*.txt` (courses, FAQs, policies, support)

---

### 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `HF_API_TOKEN` | ✅ Yes | HuggingFace API token (get one at huggingface.co/settings/tokens) |
| `LLM_PROVIDER` | No | LLM backend: `huggingface` (default), `openai`, `cohere` |
| `HF_MODEL_NAME` | No | HF model ID (default: `Qwen/Qwen2.5-7B-Instruct`) |
| `SIMILARITY_THRESHOLD` | No | Min retrieval score 0–1 (default: `0.05`) |
| `TOP_K_RETRIEVAL` | No | Number of context chunks to retrieve (default: `3`) |
| `DEBUG` | No | Enable debug logging (default: `False`) |

---

### 💬 Chat UI
A browser-based chat interface is available at **`/`** (or `/ui`).

### 📬 Support
Contact: support@academyx.abc
    """,
    version="1.0.0",
    contact={
        "name": "Academy X Support",
        "email": "support@academyx.abc",
    },
    license_info={
        "name": "UNICCON GROUP — AI Engineer Assessment",
    },
    openapi_tags=[
        {
            "name": "chat",
            "description": "Core RAG chatbot endpoints — ask questions, upload documents, check index status.",
        },
        {
            "name": "root",
            "description": "Service information and health.",
        },
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (CSS, JS, assets if any)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Include API routers
app.include_router(router)


@app.get("/", include_in_schema=False)
async def root():
    """Serve the chat UI at root."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/info", tags=["root"])
async def info():
    """API info endpoint."""
    return {
        "message": "Welcome to Academy X RAG-based LLM Chatbot",
        "version": "1.0.0",
        "docs_url": "/docs",
        "chat_ui": "/",
        "health_check": "/api/health"
    }


@app.get("/ui", include_in_schema=False)
async def chat_ui():
    """Serve the chat UI (alias for root)."""
    return FileResponse(STATIC_DIR / "index.html")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

