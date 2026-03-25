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


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    rag_service = get_rag_service()
    return HealthResponse(
        status="healthy",
        message="RAG Chatbot service is running"
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint for asking questions to the FAQ chatbot.
    
    Args:
        request: Chat request with user query
        
    Returns:
        Chat response with answer, sources, and confidence
    """
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


@router.post("/upload-documents")
async def upload_documents(files: list[UploadFile] = File(...)):
    """Upload and index documents for the FAQ knowledge base.
    
    Args:
        files: List of text files to upload and index
        
    Returns:
        Status message with number of documents indexed
    """
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


@router.get("/index-status", response_model=IndexStatusResponse)
async def index_status():
    """Get the status of the knowledge base index.
    
    Returns:
        Index status with document count
    """
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
