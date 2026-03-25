#!/usr/bin/env python
"""Setup script to initialize the knowledge base with sample FAQs."""
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.rag_service import RAGService
from data.sample_faqs import get_sample_faqs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_knowledge_base():
    """Initialize the knowledge base with sample FAQs."""
    try:
        logger.info("Initializing RAG service...")
        rag_service = RAGService()
        
        logger.info("Loading sample FAQs...")
        sample_faqs = get_sample_faqs()
        
        logger.info(f"Indexing {len(sample_faqs)} document(s)...")
        chunk_count = rag_service.index_documents(sample_faqs)
        
        # Save index
        index_path = Path("data/index.pkl")
        index_path.parent.mkdir(exist_ok=True)
        rag_service.save_index(str(index_path))
        
        logger.info(f"✓ Knowledge base initialized successfully!")
        logger.info(f"✓ Indexed {chunk_count} chunks")
        logger.info(f"✓ Index saved to {index_path}")
        
        return True
    
    except Exception as e:
        logger.error(f"Failed to initialize knowledge base: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = setup_knowledge_base()
    sys.exit(0 if success else 1)
