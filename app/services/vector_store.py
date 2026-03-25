"""Vector store and retrieval service.

Supports two backends:
  1. Primary: sentence-transformers + FAISS (GPU/CPU)
  2. Fallback: scikit-learn TF-IDF (pure Python, no PyTorch)

The fallback activates automatically when sentence-transformers
or FAISS cannot be loaded (e.g. PyTorch DLL issues on Windows,
unsupported Python versions, etc.)
"""
import pickle
import logging
from typing import List, Tuple
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

# ---------- optional heavy deps ----------
_ST_AVAILABLE = False
_FAISS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
    import torch  # force a real import so we catch DLL errors here
    _ST_AVAILABLE = True
    logger.info("sentence-transformers loaded successfully")
except Exception as _st_err:
    logger.warning(f"sentence-transformers unavailable ({_st_err}); using TF-IDF fallback")

try:
    import faiss  # type: ignore
    _FAISS_AVAILABLE = True
except Exception:
    faiss = None  # type: ignore

# ---------- TF-IDF fallback helpers ----------
try:
    from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
    from sklearn.metrics.pairwise import cosine_similarity  # type: ignore
    _SKLEARN_AVAILABLE = True
except ImportError:
    _SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available; install it for TF-IDF fallback")


class _TFIDFBackend:
    """Lightweight TF-IDF-based vector store (no PyTorch required)."""

    def __init__(self):
        self._vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words="english",
        )
        self._matrix = None
        self.documents: List[str] = []

    def add_documents(self, documents: List[str]):
        self.documents.extend(documents)
        self._matrix = self._vectorizer.fit_transform(self.documents)
        logger.info(f"TF-IDF index built with {len(self.documents)} docs")

    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        if self._matrix is None or not self.documents:
            return []
        q_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(q_vec, self._matrix).flatten()
        top_idx = scores.argsort()[::-1][:top_k]
        return [(self.documents[i], float(scores[i])) for i in top_idx if scores[i] > 0]

    def is_empty(self) -> bool:
        return not self.documents


class _FAISSBackend:
    """FAISS + sentence-transformers vector store."""

    def __init__(self, model_name: str):
        self._encoder = SentenceTransformer(model_name)
        self._dim = self._encoder.get_sentence_embedding_dimension()
        self._index = None
        self.documents: List[str] = []

    def add_documents(self, documents: List[str]):
        logger.info(f"Encoding {len(documents)} chunks with sentence-transformers…")
        embeddings = self._encoder.encode(documents, convert_to_numpy=True)
        if self._index is None:
            self._index = faiss.IndexFlatL2(self._dim)
        self._index.add(embeddings.astype(np.float32))
        self.documents.extend(documents)
        logger.info("FAISS index updated")

    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        if self._index is None or not self.documents:
            return []
        q_emb = self._encoder.encode([query], convert_to_numpy=True).astype(np.float32)
        distances, indices = self._index.search(q_emb, min(top_k, len(self.documents)))
        return [
            (self.documents[i], float(1 / (1 + d)))
            for i, d in zip(indices[0], distances[0])
            if i < len(self.documents)
        ]

    def is_empty(self) -> bool:
        return self._index is None or not self.documents


class VectorStore:
    """Unified vector store – auto-selects FAISS or TF-IDF backend."""

    def __init__(self, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialise the best available backend.

        Args:
            embedding_model: HuggingFace model name used by FAISS backend.
        """
        self._embedding_model_name = embedding_model

        if _ST_AVAILABLE and _FAISS_AVAILABLE:
            logger.info("Using FAISS + sentence-transformers backend")
            self._backend = _FAISSBackend(embedding_model)
            self._backend_type = "faiss"
        elif _SKLEARN_AVAILABLE:
            logger.info("Using TF-IDF (scikit-learn) fallback backend")
            self._backend = _TFIDFBackend()
            self._backend_type = "tfidf"
        else:
            raise RuntimeError(
                "No embedding backend available. "
                "Please install scikit-learn (pip install scikit-learn) or "
                "sentence-transformers + faiss-cpu."
            )

    # ------------------------------------------------------------------ #
    # Public API (same as before)                                          #
    # ------------------------------------------------------------------ #

    @property
    def documents(self) -> List[str]:
        return self._backend.documents

    def add_documents(self, documents: List[str]):
        """Add and index a list of text chunks."""
        if not documents:
            logger.warning("No documents provided to add")
            return
        self._backend.add_documents(documents)
        logger.info(f"Successfully indexed {len(documents)} chunks via {self._backend_type}")

    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Return top-k (document, similarity_score) tuples for *query*."""
        if self.is_empty():
            logger.warning("Vector store is empty")
            return []
        return self._backend.search(query, top_k=top_k)

    def save(self, path: str):
        """Persist the vector store to *path*."""
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "backend_type": self._backend_type,
            "embedding_model": self._embedding_model_name,
        }

        if self._backend_type == "tfidf":
            payload["vectorizer"] = self._backend._vectorizer
            payload["matrix"] = self._backend._matrix
            payload["documents"] = self._backend.documents
        else:  # faiss
            payload["index"] = self._backend._index
            payload["documents"] = self._backend.documents

        with open(save_path, "wb") as fh:
            pickle.dump(payload, fh)
        logger.info(f"Vector store saved to {save_path}")

    def load(self, path: str):
        """Load a previously saved vector store from *path*."""
        load_path = Path(path)
        if not load_path.exists():
            logger.warning(f"Index file not found: {load_path}")
            return

        with open(load_path, "rb") as fh:
            payload = pickle.load(fh)

        saved_type = payload.get("backend_type", "faiss")

        if saved_type == "tfidf" and _SKLEARN_AVAILABLE:
            backend = _TFIDFBackend()
            backend._vectorizer = payload["vectorizer"]
            backend._matrix = payload["matrix"]
            backend.documents = payload["documents"]
            self._backend = backend
            self._backend_type = "tfidf"
        elif saved_type == "faiss" and _ST_AVAILABLE and _FAISS_AVAILABLE:
            backend = _FAISSBackend(payload.get("embedding_model", self._embedding_model_name))
            backend._index = payload["index"]
            backend.documents = payload["documents"]
            self._backend = backend
            self._backend_type = "faiss"
        else:
            # Cross-backend load: re-index from raw documents using current backend
            raw_docs = payload.get("documents", [])
            logger.warning(
                f"Saved backend '{saved_type}' differs from current '{self._backend_type}'. "
                "Re-indexing documents with current backend."
            )
            if raw_docs:
                self._backend.add_documents(raw_docs)

        logger.info(f"Loaded index ({self._backend_type}) with {len(self.documents)} docs from {load_path}")

    def is_empty(self) -> bool:
        """Return True when no documents are indexed."""
        return self._backend.is_empty()
