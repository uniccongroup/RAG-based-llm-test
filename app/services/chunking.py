"""Text chunking service for document processing."""
import logging
from typing import List

logger = logging.getLogger(__name__)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Chunk text into overlapping segments.
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk
        overlap: Number of overlapping characters between chunks
        
    Returns:
        List of text chunks
    """
    if not text or chunk_size <= 0:
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        
        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)
        
        start = end - overlap if end < len(text) else len(text)
    
    logger.debug(f"Text chunked into {len(chunks)} segments")
    return chunks


def process_documents(documents: List[str], chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Process multiple documents into chunks.
    
    Args:
        documents: List of document texts
        chunk_size: Size of each chunk
        overlap: Number of overlapping characters between chunks
        
    Returns:
        List of all chunks from all documents
    """
    all_chunks = []
    
    for doc in documents:
        chunks = chunk_text(doc, chunk_size, overlap)
        all_chunks.extend(chunks)
    
    logger.info(f"Processed {len(documents)} documents into {len(all_chunks)} chunks")
    return all_chunks
