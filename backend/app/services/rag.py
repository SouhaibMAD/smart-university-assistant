"""Pipeline RAG complet : retrieval -> garde-fou -> prompt -> LLM -> sources.

Périmètre : tech lead (feature/rag-core).

Contrat appelé par la route /chat :
    answer_question(db, question, history) -> RagAnswer
`history` = derniers messages [{"role": "user"|"assistant", "content": "..."}].
"""
from pathlib import Path

from sqlalchemy.orm import Session

from app.services.types import RagAnswer

NO_ANSWER_TOKEN = "[[NO_ANSWER]]"
SYSTEM_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "system_fr.txt"


def answer_question(db: Session, question: str, history: list[dict] | None = None) -> RagAnswer:
    raise NotImplementedError("Implémenté dans feature/rag-core")
