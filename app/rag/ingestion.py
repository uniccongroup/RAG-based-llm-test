import os
import re
import logging
import asyncio
from pathlib import Path
from typing import List, Tuple
import numpy as np

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"

CHUNK_SIZE = 500          # target characters per chunk
CHUNK_OVERLAP = 80        # characters of overlap between adjacent chunks
MIN_CHUNK_SIZE = 100      # discard chunks shorter than this


def load_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_pdf(path: Path) -> str:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError(
            "PyMuPDF is required to load PDF files. "
            "Run: pip install pymupdf"
        )
    doc = fitz.open(str(path))
    pages = [page.get_text() for page in doc]
    return "\n\n".join(pages)


def load_document(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".txt":
        return load_txt(path)
    elif ext == ".pdf":
        return load_pdf(path)
    else:
        logger.warning("Unsupported file type '%s' — skipping %s", ext, path.name)
        return ""


def discover_documents() -> List[Path]:
    supported = {".txt", ".pdf"}
    docs = [p for p in DATA_DIR.iterdir() if p.suffix.lower() in supported]
    logger.info("Discovered %d document(s) in %s", len(docs), DATA_DIR)
    return docs


def _split_into_chunks(text: str) -> List[str]:
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    chunks: List[str] = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE

        if end >= len(text):
            chunk = text[start:].strip()
            if len(chunk) >= MIN_CHUNK_SIZE:
                chunks.append(chunk)
            break
        window = text[start:end]
        break_pos = -1

        para_break = window.rfind("\n\n")
        if para_break > CHUNK_SIZE // 2:
            break_pos = para_break + 2

        if break_pos == -1:
            for punct in (". ", "? ", "! ", ".\n", "?\n", "!\n"):
                sb = window.rfind(punct)
                if sb > CHUNK_SIZE // 2:
                    break_pos = sb + len(punct)
                    break

        if break_pos == -1:
            break_pos = CHUNK_SIZE

        chunk = text[start : start + break_pos].strip()
        if len(chunk) >= MIN_CHUNK_SIZE:
            chunks.append(chunk)

        start = start + break_pos - CHUNK_OVERLAP

    return chunks


def chunk_document(text: str, source_name: str) -> List[dict]:
    raw_chunks = _split_into_chunks(text)
    return [
        {"content": chunk, "source": source_name, "chunk_index": i}
        for i, chunk in enumerate(raw_chunks)
    ]

_embedding_model = None  # lazy-loaded singleton


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        import os
        
        cache_dir = os.path.join(os.path.dirname(__file__), "..", "models_cache", "embeddings")
        os.makedirs(cache_dir, exist_ok=True)
        
        logger.info("Loading embedding model 'all-MiniLM-L6-v2' into %s...", cache_dir)
        _embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2",
            cache_folder=cache_dir
        )
        logger.info("Embedding model loaded.")
    return _embedding_model


def embed_texts(texts: List[str]) -> np.ndarray:
    model = get_embedding_model()
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True,   # cosine similarity via dot product
    )
    return np.array(embeddings, dtype=np.float32)


class VectorStore:
    def __init__(self):
        self.index = None          # faiss.IndexFlatIP
        self.chunks: List[dict] = []
        self.embedding_dim: int = 0

    def build(self, chunks: List[dict]) -> None:
        """Embed all chunks and build the FAISS index."""
        import faiss

        texts = [c["content"] for c in chunks]
        logger.info("Embedding %d chunks…", len(texts))
        embeddings = embed_texts(texts)

        self.embedding_dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.index.add(embeddings)
        self.chunks = chunks
        logger.info(
            "Vector store ready: %d vectors, dim=%d",
            self.index.ntotal,
            self.embedding_dim,
        )

    def search(self, query: str, top_k: int = 3) -> List[Tuple[dict, float]]:
        if self.index is None or self.index.ntotal == 0:
            raise RuntimeError("Vector store is empty — run ingestion first.")

        q_embedding = embed_texts([query])
        scores, indices = self.index.search(q_embedding, min(top_k, self.index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append((self.chunks[idx], float(score)))
        return results

    @property
    def total_chunks(self) -> int:
        return len(self.chunks)

    @property
    def is_ready(self) -> bool:
        return self.index is not None and self.index.ntotal > 0


vector_store = VectorStore()

async def ingest_documents() -> dict:
    loop = asyncio.get_event_loop()

    def _run():
        doc_paths = discover_documents()
        if not doc_paths:
            logger.warning("No documents found in %s", DATA_DIR)
            return [], []

        all_chunks: List[dict] = []
        processed: List[str] = []

        for path in doc_paths:
            logger.info("Loading %s…", path.name)
            text = load_document(path)
            if not text.strip():
                logger.warning("Empty content for %s — skipping.", path.name)
                continue
            doc_chunks = chunk_document(text, source_name=path.name)
            logger.info("  → %d chunks from %s", len(doc_chunks), path.name)
            all_chunks.extend(doc_chunks)
            processed.append(path.name)

        if all_chunks:
            vector_store.build(all_chunks)

        return all_chunks, processed

    all_chunks, processed = await loop.run_in_executor(None, _run)

    return {
        "chunks_created": len(all_chunks),
        "documents_processed": processed,
    }
