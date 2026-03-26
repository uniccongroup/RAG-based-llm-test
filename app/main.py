"""
Company X EduTech RAG Backend - Main Application Module

This module implements a FastAPI-based RAG (Retrieval-Augmented Generation) chatbot backend
for Company X's educational FAQ system. It provides endpoints for document ingestion,
question answering, and system health monitoring.

The application uses a hybrid approach combining:
- Vector search for relevant document retrieval
- Hugging Face models for answer generation
- Asynchronous processing for improved performance

Environment Variables:
    MAX_NEW_TOKENS (int): Maximum tokens for model generation (default: 150)
    TEMPERATURE (float): Sampling temperature for generation (default: 0.7)
    TOP_P (float): Nucleus sampling parameter (default: 0.9)
    REPETITION_PENALTY (float): Penalty for token repetition (default: 1.1)
"""

import logging
import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    IngestResponse,
    SourceChunk,
)
from app.rag.ingestion import ingest_documents, vector_store
from app.rag.retrieval import retrieve
from app.rag.generation import generate_answer, get_model_name

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup / shutdown) ───────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application lifecycle events (startup and shutdown).
    
    This context manager handles:
    - Initial document ingestion on startup
    - Graceful shutdown logging
    - Error recovery (non-critical failures don't prevent server startup)
    
    Args:
        app (FastAPI): The FastAPI application instance
        
    Yields:
        None: Control returns to the application after startup tasks
        
    Note:
        If initial ingestion fails, the server continues running and
        documents can be ingested manually via the /api/ingest endpoint.
    """
    logger.info("═══ Company X RAG Backend — starting up ═══")
    try:
        summary = await ingest_documents()
        logger.info(
            "Startup ingestion complete: %d chunks from %s",
            summary["chunks_created"],
            summary["documents_processed"],
        )
    except Exception as exc:
        logger.error("Startup ingestion failed: %s", exc, exc_info=True)
        # Don't crash the server — /api/ingest can be called manually.
    yield
    logger.info("═══ Company X RAG Backend — shutting down ═══")


# ── App factory ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Company X EduTech — FAQ Chatbot API",
    description=(
        "RAG-powered FAQ chatbot for Company X. "
        "Ask any question about courses, pricing, policies, and more."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS (allow all origins for development; restrict in production) ─────────
# NOTE: Current configuration allows all origins for development.
# In production, replace "*" with specific allowed origins:
# allow_origins=["https://yourdomain.com", "https://app.yourdomain.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global exception handler ────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.
    
    Catches all unhandled exceptions, logs them with stack traces,
    and returns a consistent error response to clients.
    
    Args:
        request (Request): The incoming HTTP request
        exc (Exception): The unhandled exception
        
    Returns:
        JSONResponse: Standardized error response with 500 status code
    """    
    logger.error("Unhandled exception on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later."},
    )


# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/", tags=["General"])
async def root():
    """
    Root endpoint providing welcome message and API navigation.
    
    Returns a quick-start guide with links to documentation and main endpoints.
    
    Returns:
        Dict[str, str]: Object containing welcome message and endpoint URLs
    """
    return {
        "message": "Welcome to the Company X FAQ Chatbot API 🎓",
        "docs": "/docs",
        "health": "/health",
        "chat": "/api/chat",
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health():
    """
    Health check endpoint for monitoring system status.
    
    Returns comprehensive system health information including:
    - Vector store availability and size
    - Current model information
    - Overall system status
    
    Returns:
        HealthResponse: System health status and metrics
        
    Example:
        ```json
        {
            "status": "ok",
            "vector_store_loaded": true,
            "total_chunks": 150,
            "model": "mistralai/Mistral-7B-Instruct-v0.1"
        }
        ```
    """
    return HealthResponse(
        status="ok",
        vector_store_loaded=vector_store.is_ready,
        total_chunks=vector_store.total_chunks,
        model=get_model_name(),
    )


@app.post(
    "/api/ingest",
    response_model=IngestResponse,
    tags=["Admin"],
    summary="(Re)ingest knowledge-base documents",
)
async def ingest():
    """
    Triggers document ingestion and vector store update.
    
    Processes all documents in the configured data directory and updates
    the vector store for retrieval. Returns statistics about the ingestion process.
    
    Returns:
        IngestResponse: Ingestion statistics including chunks created and documents processed
        
    Raises:
        HTTPException: 404 if no documents are found
        HTTPException: 500 if ingestion fails due to processing errors
        
    Example:
        ```json
        {
            "status": "success",
            "chunks_created": 245,
            "documents_processed": 12
        }
        ```
    """
    try:
        summary = await ingest_documents()
    except Exception as exc:
        logger.error("Ingestion failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {exc}",
        )

    if not summary["documents_processed"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No documents found in app/data/. Add .txt or .pdf files and retry.",
        )

    return IngestResponse(
        status="success",
        chunks_created=summary["chunks_created"],
        documents_processed=summary["documents_processed"],
    )


@app.post(
    "/api/chat",
    response_model=ChatResponse,
    tags=["Chatbot"],
    summary="Ask the Company X FAQ chatbot a question",
)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for answering user questions.
    
    Implements the RAG pipeline:
    1. Validates input and vector store readiness
    2. Retrieves relevant document chunks
    3. Generates answer using the LLM with context
    4. Returns answer with sources and metadata
    
    Args:
        request (ChatRequest): Chat request containing question and optional parameters
        
    Returns:
        ChatResponse: Generated answer with sources and session information
        
    Raises:
        HTTPException: 422 if question is empty or retrieval fails validation
        HTTPException: 503 if vector store is not ready
        HTTPException: 500 if answer generation fails
    """
    # validation for empty question
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Question cannot be empty"
        )
    
    # ── Guard: vector store must be ready ───────────────────────────────────
    if not vector_store.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "The knowledge base is not yet loaded. "
                "Please wait a moment and retry, or call POST /api/ingest."
            ),
        )

    session_id = request.session_id or str(uuid.uuid4())

    # ── Step 1: Retrieve ─────────────────────────────────────────────────────
    try:
        source_chunks: list[SourceChunk] = retrieve(
            query=request.question,
            top_k=request.top_k,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    # ── Step 2: Generate ─────────────────────────────────────────────────────
    try:
        answer = await generate_answer(
            question=request.question,
            context_chunks=source_chunks,
        )
    except Exception as exc:
        logger.error("LLM generation failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Answer generation failed: {exc}",
        )

    logger.info(
        "Chat | session=%s | q='%s…' | sources=%d | answer_len=%d",
        session_id,
        request.question[:50],
        len(source_chunks),
        len(answer),
    )

    return ChatResponse(
        answer=answer,
        sources=source_chunks,
        session_id=session_id,
        model_used=get_model_name(),
    )

@app.get("/api/model-info", tags=["Admin"])
async def model_info():
    """
    Get detailed information about the currently loaded language model.
    
    Returns configuration and status of the model used for answer generation,
    including the configured model name, currently loaded model, and
    inference parameters.
    
    Returns:
        Dict[str, Any]: Model information containing:
            - configured_model: Model specified in environment/config
            - loaded_model: Currently loaded model (may differ if lazy loading)
            - provider: Model provider (e.g., "huggingface")
            - parameters: Current inference parameters
            
    Example:
        ```json
        {
            "configured_model": "mistralai/Mistral-7B-Instruct-v0.1",
            "loaded_model": "mistralai/Mistral-7B-Instruct-v0.1",
            "provider": "huggingface",
            "parameters": {
                "max_new_tokens": 150,
                "temperature": 0.7,
                "top_p": 0.9,
                "repetition_penalty": 1.1
            }
        }
        ```
    """
    from app.rag.generation import _current_model_name, HF_MODEL_NAME
    
    return {
        "configured_model": HF_MODEL_NAME,
        "loaded_model": _current_model_name or "not loaded yet",
        "provider": "huggingface",
        "parameters": {
            "max_new_tokens": int(os.getenv("MAX_NEW_TOKENS", "150")),
            "temperature": float(os.getenv("TEMPERATURE", "0.7")),
            "top_p": float(os.getenv("TOP_P", "0.9")),
            "repetition_penalty": float(os.getenv("REPETITION_PENALTY", "1.1"))
        }
    }

"""
Development Server Command
--------------------------
To run the application in development mode with auto-reload:

    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

For production deployment, consider:
- Using Gunicorn with Uvicorn workers
- Setting appropriate CORS origins
- Configuring proper logging
- Using environment variables for sensitive configuration
"""