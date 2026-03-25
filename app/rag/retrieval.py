import logging
from typing import List

from app.rag.ingestion import vector_store
from app.models.schemas import SourceChunk

logger = logging.getLogger(__name__)


def retrieve(query: str, top_k: int = 3) -> List[SourceChunk]:
    query = query.strip()
    if not query:
        raise ValueError("Query must not be empty.")

    if not vector_store.is_ready:
        raise RuntimeError(
            "Vector store is not initialised. "
            "Call /api/ingest or wait for startup ingestion to complete."
        )

    raw_results = vector_store.search(query, top_k=top_k)

    chunks: List[SourceChunk] = []
    for chunk_dict, score in raw_results:
        normalised_score = max(0.0, min(1.0, (float(score) + 1.0) / 2.0))

        chunks.append(
            SourceChunk(
                content=chunk_dict["content"],
                source=chunk_dict["source"],
                score=round(normalised_score, 4),
            )
        )

    logger.debug(
        "Retrieved %d chunks for query '%s…'  top-score=%.3f",
        len(chunks),
        query[:60],
        chunks[0].score if chunks else 0.0,
    )

    return chunks
