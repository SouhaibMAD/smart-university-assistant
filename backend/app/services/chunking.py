"""Découpage du texte en chunks.

Périmètre : Siham (feature/db-ingestion).

Contrat (NE PAS MODIFIER les signatures) :
- chunk_text(text, chunk_size, overlap) -> list[str]
- chunk_pages(pages, chunk_size, overlap) -> list[ChunkDraft]
"""
from app.services.types import ChunkDraft, PageText


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    raise NotImplementedError


def chunk_pages(pages: list[PageText], chunk_size: int, overlap: int) -> list[ChunkDraft]:
    raise NotImplementedError
