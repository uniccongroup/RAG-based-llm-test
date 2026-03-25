"""Core configuration management."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # App Config
    app_name: str = "UNICCON RAG Chatbot"
    debug: bool = False
    log_level: str = "INFO"
    
    # Server Config
    host: str = "0.0.0.0"
    port: int = 8000
    
    # LLM Configuration
    llm_provider: str = "huggingface"  # Options: huggingface, openai, cohere
    hf_model_name: str = "mistralai/Mistral-7B-Instruct-v0.1"
    hf_api_token: Optional[str] = None
    openai_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    
    # Embedding Configuration
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # RAG Configuration
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_retrieval: int = 3
    similarity_threshold: float = 0.5
    
    # Paths
    data_dir: str = "data"
    logs_dir: str = "logs"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
