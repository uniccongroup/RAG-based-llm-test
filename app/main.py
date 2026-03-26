# app/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles         
from fastapi.responses import FileResponse 
from pydantic import BaseModel, Field
from app.rag import get_rag_chain, answer_question
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)


# Startup / shutdown 

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan function to handle startup and shutdown events.
    Initializes the RAG chain once at startup and logs lifecycle events.
    """
    logger.info("Starting BrightPath RAG Chatbot...")
    get_rag_chain()          # warms the chain once at startup
    logger.info("Application ready.")
    yield
    logger.info("Shutting down.")


# App 

app = FastAPI(
    title="BrightPath Academy FAQ Chatbot",
    description="RAG-powered student support chatbot for BrightPath Academy",
    version="1.0.0",
    lifespan=lifespan
)

# CORS — allows the frontend or Swagger UI to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # I shall tighten this to fit the frontend domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the static folder 
app.mount("/static", StaticFiles(directory="static"), name="static")  


# Request / Response models — pydantic models for validation and documentation

class ChatRequest(BaseModel):
    """
    Model for the chat request payload.
    """
    question: str = Field(
        ...,
        #min_length=0,
        #max_length=500,
        description="The student's question"
    )
    session_id: str = Field(
        default="default",
        description="Optional session identifier for tracking"
    )

class ChatResponse(BaseModel):
    """
    Model for the chat response payload.
    """
    answer: str
    success: bool
    session_id: str


# Endpoints 

# Serve the UI at the root URL 
@app.get("/")                                                          
def root():
    return FileResponse("static/brightpath_chatbot.html")


@app.get("/health")
def health():
    """Render and uptime monitors call this to check the service is alive."""
    return {
        "status": "healthy",
        "message": "BrightPath Academy FAQ Chatbot API is running"
        }


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Submit a customer question and receive an answer grounded
    in the BrightPath Academy knowledge base.
    
    Args:
        request (ChatRequest): 
        The incoming request containing the student's question and an optional session ID.
        
    Returns:
        ChatResponse: The response containing the answer and metadata.
    """

    logger.info(f"[Request ID: {request.session_id}] | Question contains: {len(request.question)} chars")

    result = answer_question(request.question)
    

    # Log outcome
    if result["success"]:
        logger.info(f"[{request.session_id}] Request completed successfully")
    else:
        logger.warning(f"[{request.session_id}] Request failed — check rag.py logs for details")

    return ChatResponse(
        answer=result["answer"],
        success=result["success"],
        session_id=request.session_id
    )

