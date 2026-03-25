"""Vector store and retrieval service."""
import os
import pickle
import logging
from typing import List, Tuple
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np

try:
    import faiss
except ImportError:
    faiss = None

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector store for document embeddings using FAISS."""
    
    def __init__(self, embedding_model: str):
        """Initialize vector store with embedding model.
        
        Args:
            embedding_model: Name of the embedding model to use
        """
        self.embedding_model = SentenceTransformer(embedding_model)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        self.index = None
        self.documents = []
        self.document_chunks = []
        
    def add_documents(self, documents: List[str]):
        """Add documents to the vector store.
        
        Args:
            documents: List of document texts to add
        """
        if not documents:
            logger.warning("No documents provided to add")
            return
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(documents)} documents...")
        embeddings = self.embedding_model.encode(documents, convert_to_numpy=True)
        
        # Create FAISS index
        if self.index is None:
            self.index = faiss.IndexFlatL2(self.embedding_dim)
        
        # Add embeddings to index
        self.index.add(embeddings.astype(np.float32))
        self.documents.extend(documents)
        
        logger.info(f"Successfully indexed {len(documents)} documents")
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Search for similar documents.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of (document, score) tuples
        """
        if self.index is None or len(self.documents) == 0:
            logger.warning("Vector store is empty, returning empty results")
            return []
        
        # Encode query
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        
        # Search index
        distances, indices = self.index.search(query_embedding.astype(np.float32), min(top_k, len(self.documents)))
        
        # Return results with similarity scores
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                # Convert L2 distance to similarity score
                similarity = 1 / (1 + distance)
                results.append((self.documents[idx], float(similarity)))
        
        return results
    
    def save(self, path: str):
        """Save vector store to disk.
        
        Args:
            path: Path to save the vector store
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'index': self.index,
            'documents': self.documents,
        }
        
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        
        logger.info(f"Vector store saved to {path}")
    
    def load(self, path: str):
        """Load vector store from disk.
        
        Args:
            path: Path to load the vector store from
        """
        path = Path(path)
        if not path.exists():
            logger.warning(f"Vector store file not found at {path}")
            return
        
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        self.index = data['index']
        self.documents = data['documents']
        
        logger.info(f"Vector store loaded from {path} with {len(self.documents)} documents")
    
    def is_empty(self) -> bool:
        """Check if vector store is empty."""
        return self.index is None or len(self.documents) == 0
