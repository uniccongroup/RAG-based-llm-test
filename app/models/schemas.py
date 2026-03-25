"""Data models for request/response."""
from pydantic import BaseModel, Field
from typing import Optional, List


class ChatRequest(BaseModel):
    """Chat request model."""
    query: str = Field(..., description="User question")
    session_id: Optional[str] = Field(None, description="Optional session ID for conversation tracking")


class ChatResponse(BaseModel):
    """Chat response model."""
    query: str = Field(..., description="User query")
    answer: str = Field(..., description="LLM-generated answer")
    sources: List[str] = Field(default_factory=list, description="Source documents used")
    confidence: float = Field(default=0.0, description="Confidence score of the answer")
    session_id: Optional[str] = Field(None, description="Session ID")


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Status of the application")
    message: str = Field(..., description="Status message")


class IndexStatusResponse(BaseModel):
    """Index status response model."""
    indexed: bool = Field(..., description="Whether the knowledge base is indexed")
    document_count: int = Field(..., description="Number of indexed documents")
    message: str = Field(..., description="Status message")
