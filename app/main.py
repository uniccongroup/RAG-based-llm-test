"""Main FastAPI application."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.router import router
from app.core.config import settings
from app.core.logger import logger

# Configure logging
logging.basicConfig(level=settings.log_level)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="RAG-based LLM FAQ Chatbot for Company X",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to UNICCON RAG-based LLM Chatbot",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_check": "/api/health"
    }


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
