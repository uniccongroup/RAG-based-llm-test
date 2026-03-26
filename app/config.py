# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings.
    """
    google_api_key: str               # required — fails loudly if missing
    astra_db_api_endpoint: str        # required
    astra_db_application_token: str   # required
    astra_db_namespace: str = "default_keyspace"
    astra_db_collection: str = "brightpath_rag"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()   # ensures variables are validated immediately on import