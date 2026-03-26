"""Chat API endpoints."""
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from app.models.schemas import ChatRequest, ChatResponse, HealthResponse, IndexStatusResponse
from app.services.rag_service import RAGService
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])

# Global RAG service instance
rag_service = None


def get_rag_service() -> RAGService:
    """Get or create RAG service instance."""
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
        # Try to load existing index
        index_path = Path("data/index.pkl")
        if index_path.exists():
            rag_service.load_index(str(index_path))
    return rag_service


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check whether the Academy X RAG Chatbot service is up and running. Use this to verify deployment status before sending queries.",
    responses={
        200: {"description": "Service is healthy and ready to accept requests."},
        500: {"description": "Service is unavailable."},
    },
)
async def health_check():
    """Returns the current health status of the service."""
    rag_service = get_rag_service()
    return HealthResponse(
        status="healthy",
        message="RAG Chatbot service is running"
    )


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Ask a Question",
    description="""
Send a natural language question and receive an AI-generated answer grounded in the Academy X knowledge base.

**How it works:**
1. The query is matched against the TF-IDF index to retrieve the most relevant knowledge base chunks.
2. The retrieved chunks are passed as context to the `Qwen/Qwen2.5-7B-Instruct` LLM.
3. The LLM synthesises a conversational answer — it does **not** copy text verbatim.

**Example queries:**
- `"What courses does Academy X offer?"`
- `"How do I enrol in the Cybersecurity track?"`
- `"What is the refund policy?"`
- `"How much does the Data Science program cost?"`

**Notes:**
- Greetings like `"Hi"` or `"Hello"` are handled gracefully without hitting the LLM.
- If no relevant context is found, a warm fallback message is returned.
    """,
    responses={
        200: {"description": "Successfully generated an answer."},
        400: {"description": "Query is empty or invalid."},
        503: {"description": "Knowledge base is not yet indexed. Run `setup_kb.py` first."},
        500: {"description": "Internal server error during generation."},
    },
)
async def chat(request: ChatRequest):
    """RAG pipeline: retrieve relevant chunks → generate answer with Qwen2.5-7B."""
    try:
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        logger.info(f"Received chat request: {request.query}")
        
        rag_service = get_rag_service()
        
        # Check if knowledge base is indexed
        if not rag_service.is_indexed():
            raise HTTPException(
                status_code=503,
                detail="Knowledge base is not indexed. Please upload documents first."
            )
        
        # Generate answer
        answer, sources, confidence = rag_service.answer_question(request.query)
        
        return ChatResponse(
            query=request.query,
            answer=answer,
            sources=sources,
            confidence=confidence,
            session_id=request.session_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/upload-documents",
    summary="Upload & Index Documents",
    description="""
Upload one or more `.txt` documents to extend or replace the Academy X knowledge base.

Uploaded files are:
1. Decoded as UTF-8 text
2. Split into 500-character overlapping chunks
3. Indexed into the TF-IDF vector store
4. Persisted to `data/index.pkl`

**Supported formats:** `text/plain` (`.txt`), `text/markdown` (`.md`)

**Tip:** After uploading, the chatbot immediately uses the new content — no restart required.
    """,
    responses={
        200: {"description": "Documents indexed successfully."},
        400: {"description": "No files provided or no valid documents found."},
        500: {"description": "Error during indexing."},
    },
)
async def upload_documents(files: list[UploadFile] = File(...)):
    """Upload .txt files and rebuild the TF-IDF knowledge base index."""
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        documents = []
        
        for file in files:
            if file.content_type not in ["text/plain", "application/pdf", "text/markdown"]:
                logger.warning(f"Skipping file {file.filename}: unsupported type {file.content_type}")
                continue
            
            content = await file.read()
            text = content.decode('utf-8', errors='ignore')
            
            if text.strip():
                documents.append(text)
                logger.info(f"Loaded document: {file.filename}")
        
        if not documents:
            raise HTTPException(status_code=400, detail="No valid documents to process")
        
        # Index documents
        rag_service = get_rag_service()
        chunk_count = rag_service.index_documents(documents)
        
        # Save index to disk
        index_path = Path("data/index.pkl")
        index_path.parent.mkdir(exist_ok=True)
        rag_service.save_index(str(index_path))
        
        logger.info(f"Successfully indexed {chunk_count} chunks from {len(documents)} documents")
        
        return {
            "status": "success",
            "message": f"Successfully indexed {chunk_count} chunks from {len(documents)} documents",
            "document_count": len(documents),
            "chunk_count": chunk_count
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error uploading documents: {str(e)}")


@router.get(
    "/index-status",
    response_model=IndexStatusResponse,
    summary="Knowledge Base Index Status",
    description="""
Check whether the knowledge base vector index has been built and is ready to serve queries.

If `indexed` is `false`, the chatbot cannot answer questions. Fix by either:
- Running `python setup_kb.py` locally
- Calling `POST /api/upload-documents` with your `.txt` files

The `document_count` reflects the number of **chunks** (not files) currently in the index.
    """,
    responses={
        200: {"description": "Index status returned successfully."},
        500: {"description": "Error retrieving index status."},
    },
)
async def index_status():
    """Returns whether the TF-IDF index is built and how many chunks it contains."""
    try:
        rag_service = get_rag_service()
        
        if rag_service.is_indexed():
            return IndexStatusResponse(
                indexed=True,
                document_count=rag_service.get_document_count(),
                message=f"Knowledge base is indexed with {rag_service.get_document_count()} documents"
            )
        else:
            return IndexStatusResponse(
                indexed=False,
                document_count=0,
                message="Knowledge base is not indexed"
            )
    
    except Exception as e:
        logger.error(f"Error getting index status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting index status: {str(e)}")
