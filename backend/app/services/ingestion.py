"""Extraction du texte (PDF/TXT) et ingestion en base.

Périmètre : Siham (feature/db-ingestion).

Contrat (NE PAS MODIFIER les signatures) :
- extract_pages(data, filename) -> list[PageText]
- ingest_document(db, data, filename, uploaded_by, embed_fn=None) -> Document
  `embed_fn` : fonction (list[str]) -> list[list[float]] ; par défaut
  services.embeddings.embed_passages. Les tests injectent un faux embed_fn.
"""
from collections.abc import Callable
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from app.services.types import PageText

if TYPE_CHECKING:
    from app.db.models import Document


class DuplicateDocumentError(Exception):
    """Un document avec le même SHA-256 existe déjà."""


class UnreadableDocumentError(Exception):
    """Fichier vide, illisible, type non supporté, ou PDF scanné sans texte."""


def extract_pages(data: bytes, filename: str) -> list[PageText]:
    raise NotImplementedError


def ingest_document(
    db: Session,
    data: bytes,
    filename: str,
    uploaded_by: int | None,
    embed_fn: Callable[[list[str]], list[list[float]]] | None = None,
) -> "Document":
    raise NotImplementedError
