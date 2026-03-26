"""
Vector Store Cache Module

This module provides persistent storage for the FAISS vector index and associated document chunks.
It enables the application to:
- Cache embeddings between server restarts
- Avoid regenerating embeddings for unchanged documents
- Reduce startup time and API costs

The cache is stored in a pickle file in the models_cache directory,
which is created automatically if it doesn't exist.

File Structure:
    models_cache/
        vector_store.pkl    # Pickled dictionary containing FAISS index and chunks

Usage Example:
    from app.rag.cache import save_vector_store, load_vector_store
    
    # Save vector store
    save_vector_store(faiss_index, document_chunks)
    
    # Load vector store
    index, chunks = load_vector_store()
    if index is not None:
        print(f"Loaded {len(chunks)} chunks from cache")
"""

import pickle
import os
from pathlib import Path

from fastapi import logger

CACHE_DIR = Path(__file__).parent.parent / "models_cache"
CACHE_DIR.mkdir(exist_ok=True)

def save_vector_store(index, chunks):
    """
    Persist FAISS vector index and document chunks to disk.
    
    This function serializes the FAISS index and associated chunks using pickle,
    saving them to a predefined cache location. The cached data can be reloaded
    on subsequent application starts to avoid recomputing embeddings.
    
    Args:
        index: FAISS index object containing document embeddings.
               This can be any picklable FAISS index type (e.g., IndexFlatIP, IndexIVFFlat).
        chunks (list): List of document chunks with their metadata.
                       Each chunk should be a dictionary or object containing:
                       - text: The chunk content
                       - metadata: Source document info, page numbers, etc.
    
    Raises:
        pickle.PickleError: If serialization fails due to non-picklable objects
        IOError: If file writing fails (permissions, disk space, etc.)
    
    Example:
        >>> index = faiss.IndexFlatIP(768)  # 768-dim embeddings
        >>> chunks = [
        ...     {"text": "Course starts in January", "metadata": {"source": "faq.pdf"}},
        ...     {"text": "Price is $299", "metadata": {"source": "pricing.pdf"}}
        ... ]
        >>> save_vector_store(index, chunks)
        INFO: Vector store saved to /path/to/models_cache/vector_store.pkl
    
    Notes:
        - The cache file is overwritten on each call
        - For large indexes (>1GB), consider implementing incremental saves
        - The FAISS index must be picklable (standard FAISS indexes are)
    """
    cache_path = CACHE_DIR / "vector_store.pkl"
    with open(cache_path, 'wb') as f:
        pickle.dump({'index': index, 'chunks': chunks}, f)
    logger.info(f"Vector store saved to {cache_path}")

def load_vector_store():
    """
    Load FAISS vector index and document chunks from disk cache.
    
    Attempts to restore previously cached vector store data. If the cache file
    doesn't exist or is corrupted, returns (None, None) to signal that fresh
    ingestion is required.
    
    Returns:
        Tuple[Optional[Any], Optional[list]]: A tuple containing:
            - index: The deserialized FAISS index object, or None if not available
            - chunks: List of document chunks, or None if not available
    
    Raises:
        pickle.UnpicklingError: If the cache file is corrupted or incompatible
        EOFError: If the cache file is truncated or empty
        IOError: If file reading fails (permissions, etc.)
    
    Example:
        >>> index, chunks = load_vector_store()
        >>> if index is not None:
        ...     print(f"Loaded cache with {len(chunks)} chunks")
        ... else:
        ...     print("No cache found, performing fresh ingestion")
    
    Notes:
        - Cache compatibility depends on Python version and FAISS version
        - Consider adding version checking for production deployments
        - Large indexes may take several seconds to load
    """
    cache_path = CACHE_DIR / "vector_store.pkl"
    if cache_path.exists():
        with open(cache_path, 'rb') as f:
            data = pickle.load(f)
        return data['index'], data['chunks']
    return None, None
