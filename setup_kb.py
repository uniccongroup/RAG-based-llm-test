#!/usr/bin/env python
"""Setup script to initialize the knowledge base from .txt files in data/."""
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.rag_service import RAGService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"


def load_txt_files() -> list:
    """Load all .txt documents from the data/ directory."""
    docs = []
    txt_files = sorted(DATA_DIR.glob("*.txt"))
    if not txt_files:
        logger.warning("No .txt files found in data/ – knowledge base will be empty!")
        return docs
    for txt_file in txt_files:
        text = txt_file.read_text(encoding="utf-8", errors="ignore").strip()
        if text:
            docs.append(text)
            logger.info(f"  Loaded: {txt_file.name} ({len(text):,} chars)")
        else:
            logger.warning(f"  Skipped (empty): {txt_file.name}")
    return docs


def setup_knowledge_base():
    """Initialize the knowledge base exclusively from data/*.txt files."""
    try:
        logger.info("Initializing RAG service...")
        rag_service = RAGService()

        logger.info(f"Scanning {DATA_DIR} for .txt files...")
        all_documents = load_txt_files()

        logger.info(f"Indexing {len(all_documents)} document(s) total...")
        chunk_count = rag_service.index_documents(all_documents)
        
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
