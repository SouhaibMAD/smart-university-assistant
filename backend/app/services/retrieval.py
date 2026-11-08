"""Recherche des passages pertinents (pgvector, similarité cosinus).

Périmètre : tech lead (feature/rag-core).
"""
from sqlalchemy.orm import Session

from app.services.types import RetrievedChunk


def retrieve(
    db: Session, query: str, top_k: int | None = None, min_score: float | None = None
) -> list[RetrievedChunk]:
    raise NotImplementedError("Implémenté dans feature/rag-core")
