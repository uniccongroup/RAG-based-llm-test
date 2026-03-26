"""Data models for request/response."""
from pydantic import BaseModel, Field
from typing import Optional, List


class ChatRequest(BaseModel):
    """Payload for asking the Academy X chatbot a question."""
    query: str = Field(
        ...,
        description="The natural language question to ask the chatbot.",
        examples=["What courses does Academy X offer?", "How do I enrol in the Cybersecurity track?"],
        min_length=1,
        max_length=1000,
    )
    session_id: Optional[str] = Field(
        None,
        description="Optional session identifier for conversation tracking. Can be any string.",
        examples=["user-abc-123"],
    )


class ChatResponse(BaseModel):
    """Response from the RAG chatbot pipeline."""
    query: str = Field(..., description="The original question that was asked.")
    answer: str = Field(..., description="AI-generated answer synthesised from the knowledge base.")
    sources: List[str] = Field(
        default_factory=list,
        description="Excerpts from the knowledge base chunks used to generate the answer.",
    )
    confidence: float = Field(
        default=0.0,
        description="Retrieval confidence score (0.0–1.0). Higher means the knowledge base had more relevant content.",
        ge=0.0,
        le=1.0,
    )
    session_id: Optional[str] = Field(None, description="Echo of the session ID from the request, if provided.")


class HealthResponse(BaseModel):
    """Service health status."""
    status: str = Field(..., description="'healthy' if the service is running correctly.", examples=["healthy"])
    message: str = Field(..., description="Human-readable status message.", examples=["RAG Chatbot service is running"])


class IndexStatusResponse(BaseModel):
    """Status of the TF-IDF knowledge base index."""
    indexed: bool = Field(..., description="True if the vector index has been built and is ready to serve queries.")
    document_count: int = Field(..., description="Number of text chunks currently in the index (not the number of source files).")
    message: str = Field(..., description="Human-readable summary of the index state.")
