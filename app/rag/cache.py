import pickle
import os
from pathlib import Path

from fastapi import logger

CACHE_DIR = Path(__file__).parent.parent / "models_cache"
CACHE_DIR.mkdir(exist_ok=True)

def save_vector_store(index, chunks):
    """Save FAISS index and chunks to disk."""
    cache_path = CACHE_DIR / "vector_store.pkl"
    with open(cache_path, 'wb') as f:
        pickle.dump({'index': index, 'chunks': chunks}, f)
    logger.info(f"Vector store saved to {cache_path}")

def load_vector_store():
    """Load FAISS index and chunks from disk."""
    cache_path = CACHE_DIR / "vector_store.pkl"
    if cache_path.exists():
        with open(cache_path, 'rb') as f:
            data = pickle.load(f)
        return data['index'], data['chunks']
    return None, None
