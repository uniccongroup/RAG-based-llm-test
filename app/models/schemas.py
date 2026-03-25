from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The user's question for the FAQ chatbot",
        examples=["What courses does Company X offer?"]
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Optional session ID for tracking conversations"
    )
    top_k: Optional[int] = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of relevant document chunks to retrieve"
    )


class SourceChunk(BaseModel):
    content: str = Field(description="The text content of the retrieved chunk")
    source: str = Field(description="Source document name")
    score: float = Field(description="Relevance score (0-1, higher = more relevant)")


class ChatResponse(BaseModel):
    answer: str = Field(description="The LLM-generated answer")
    sources: List[SourceChunk] = Field(
        default_factory=list,
        description="Retrieved document chunks used to generate the answer"
    )
    session_id: Optional[str] = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    model_used: str = Field(description="The LLM model that generated the response")


class HealthResponse(BaseModel):
    status: str
    vector_store_loaded: bool
    total_chunks: int
    model: str


class IngestResponse(BaseModel):
    status: str
    chunks_created: int
    documents_processed: List[str]
