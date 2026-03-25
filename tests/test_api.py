import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.schemas import SourceChunk


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_source_chunks():
    return [
        SourceChunk(
            content="Company X offers courses in Web Development, Data Science, and more.",
            source="company_x_faq.txt",
            score=0.92,
        )
    ]


@pytest.fixture
def mock_ready_vector_store():
    """Patch the vector store to appear ready."""
    with patch("app.main.vector_store") as mock_vs:
        mock_vs.is_ready = True
        mock_vs.total_chunks = 42
        yield mock_vs


# ── Health endpoint ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "vector_store_loaded" in body
    assert "total_chunks" in body
    assert "model" in body


# ── Root endpoint ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_root_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert "Company X" in response.json()["message"]


# ── Chat endpoint ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_chat_returns_answer(mock_ready_vector_store, mock_source_chunks):
    with (
        patch("app.main.retrieve", return_value=mock_source_chunks),
        patch(
            "app.main.generate_answer",
            new=AsyncMock(return_value="Company X offers Web Development and Data Science."),
        ),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/chat",
                json={"question": "What courses does Company X offer?"},
            )

    assert response.status_code == 200
    body = response.json()
    assert "answer" in body
    assert len(body["answer"]) > 0
    assert "sources" in body
    assert "session_id" in body
    assert "model_used" in body


@pytest.mark.asyncio
async def test_chat_empty_question_rejected():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/api/chat", json={"question": ""})

    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_chat_503_when_store_not_ready():
    with patch("app.main.vector_store") as mock_vs:
        mock_vs.is_ready = False
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/chat",
                json={"question": "What is the refund policy?"},
            )

    assert response.status_code == 503


# ── Ingest endpoint ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ingest_endpoint():
    mock_summary = {
        "chunks_created": 35,
        "documents_processed": ["company_x_faq.txt"],
    }
    with patch("app.main.ingest_documents", new=AsyncMock(return_value=mock_summary)):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post("/api/ingest")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["chunks_created"] == 35
    assert "company_x_faq.txt" in body["documents_processed"]
