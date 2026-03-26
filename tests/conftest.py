"""
conftest.py — shared fixtures used across all test files.

All external services (AstraDB, Gemini, HuggingFace) are mocked here
so tests run offline with no API keys and no network calls.
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


# ── Mock environment variables ────────────────────────────────────────────────
# These must be patched before app modules are imported so pydantic-settings
# does not throw a ValidationError for missing required fields.

import os
os.environ.setdefault("GOOGLE_API_KEY", "fake-google-key-for-testing")
os.environ.setdefault("ASTRA_DB_API_ENDPOINT", "https://fake-endpoint.apps.astra.datastax.com")
os.environ.setdefault("ASTRA_DB_APPLICATION_TOKEN", "AstraCS:faketoken123")
os.environ.setdefault("ASTRA_DB_NAMESPACE", "default_keyspace")
os.environ.setdefault("ASTRA_DB_COLLECTION", "brightpath_rag")


# ── Shared mock document ──────────────────────────────────────────────────────

def make_mock_doc(content: str, source: str = "01_BrightPath_FAQs.docx", chunk_index: int = 0):
    """Helper that creates a mock LangChain Document object."""
    doc = MagicMock()
    doc.page_content = content
    doc.metadata = {"source": source, "chunk_index": chunk_index}
    return doc


# ── FastAPI test client fixture ───────────────────────────────────────────────

@pytest.fixture(scope="session")
def mock_rag_components():
    """
    Session-scoped fixture that patches all external services for the
    entire test session. Returns the mock objects so individual tests
    can customise return values.
    """
    with patch("langchain_huggingface.HuggingFaceEmbeddings") as mock_embeddings, \
         patch("langchain_astradb.AstraDBVectorStore") as mock_vector_store, \
         patch("langchain_google_genai.ChatGoogleGenerativeAI") as mock_llm:

        # Configure embeddings mock
        mock_embeddings.return_value = MagicMock()

        # Configure vector store mock with a retriever that returns sample docs
        mock_retriever = MagicMock()
        mock_retriever.invoke.return_value = [
            make_mock_doc(
                "Learners enrolled in self-paced courses are entitled to a full refund "
                "within 7 calendar days of their enrolment date.",
                source="03_BrightPath_Student_Policies.docx",
                chunk_index=2
            ),
            make_mock_doc(
                "BrightPath Academy accepts Visa, Mastercard, PayPal, and bank transfer.",
                source="01_BrightPath_FAQs.docx",
                chunk_index=1
            )
        ]
        mock_vs_instance = MagicMock()
        mock_vs_instance.as_retriever.return_value = mock_retriever
        mock_vector_store.return_value = mock_vs_instance

        # Configure LLM mock
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance

        yield {
            "embeddings": mock_embeddings,
            "vector_store": mock_vector_store,
            "retriever": mock_retriever,
            "llm": mock_llm_instance,
        }


@pytest.fixture(scope="session")
def client(mock_rag_components):
    """
    FastAPI TestClient — used for all endpoint tests.
    Chain is pre-warmed using mocked components.
    """
    # Clear lru_cache so tests get fresh instances with mocked components
    from app.rag import get_embeddings, get_vector_store, get_retriever, get_rag_chain
    get_embeddings.cache_clear()
    get_vector_store.cache_clear()
    get_retriever.cache_clear()
    get_rag_chain.cache_clear()

    from app.main import app
    return TestClient(app)
