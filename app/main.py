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
    description="RAG-based LLM FAQ Chatbot for Academy X",
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

# Serve static files (CSS, JS, assets if any)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Include API routers
app.include_router(router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint — API welcome message."""
    return {
        "message": "Welcome to Academy X RAG-based LLM Chatbot",
        "version": "1.0.0",
        "docs_url": "/docs",
        "chat_ui": "/ui",
        "health_check": "/api/health"
    }


@app.get("/ui", include_in_schema=False)
async def chat_ui():
    """Serve the chat UI."""
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

