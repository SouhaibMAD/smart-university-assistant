"""Types partagés entre les services. Propriété du tech lead."""
from dataclasses import dataclass, field


@dataclass
class PageText:
    page: int | None  # None pour un fichier TXT
    text: str


@dataclass
class ChunkDraft:
    chunk_index: int
    page: int | None
    content: str


@dataclass
class RetrievedChunk:
    chunk_id: int
    document_id: int
    document_name: str
    page: int | None
    content: str
    score: float  # similarité cosinus, entre 0 et 1


@dataclass
class RagAnswer:
    answer: str
    answered: bool
    sources: list[RetrievedChunk] = field(default_factory=list)
