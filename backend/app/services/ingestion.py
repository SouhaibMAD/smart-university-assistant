import hashlib
from collections.abc import Callable
from pathlib import Path

import pymupdf
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Chunk, Document
from app.services.chunking import chunk_pages
from app.services.types import PageText


class DuplicateDocumentError(Exception):
    pass

class UnreadableDocumentError(Exception):
    pass

def extract_pages(data: bytes, filename: str) -> list[PageText]:
    if not data:
        raise UnreadableDocumentError("Le fichier est vide.")

    extension = Path(filename).suffix.lower()

    if extension == ".txt":
        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = data.decode("latin-1")

        text = text.strip()

        if not text:
            raise UnreadableDocumentError(
                "Le fichier TXT ne contient aucun texte exploitable."
            )

        return [PageText(page=None, text=text)]


    if extension == ".pdf":
        try:
            with pymupdf.open(stream=data, filetype="pdf") as pdf:
                pages = []

                for page_number, pdf_page in enumerate(pdf, start=1):
                    text = pdf_page.get_text("text").strip()

                    if text:
                        pages.append(
                            PageText(page=page_number, text=text)
                        )

                if not pages:
                    raise UnreadableDocumentError(
                        "Le PDF ne contient aucun texte extractible. "
                        "Il est peut-Ãªtre scannÃ©."
                    )

                return pages

        except UnreadableDocumentError:
            raise
        except Exception as exc:
            raise UnreadableDocumentError(
                "Impossible de lire le fichier PDF."
            ) from exc


    raise UnreadableDocumentError(
        f"Format non supportÃ© : {extension or 'inconnu'}. "
        "Formats acceptÃ©s : PDF et TXT."
    )



def ingest_document(
    db: Session,
    data: bytes,
    filename: str,
    uploaded_by: int | None,
    embed_fn: Callable[[list[str]], list[list[float]]] | None = None,
) -> "Document":


    settings = get_settings()
    sha256 = hashlib.sha256(data).hexdigest()
    file_type = Path(filename).suffix.lower().lstrip(".")

    existing = db.scalar(
        select(Document).where(Document.sha256 == sha256)
    )
    if existing is not None:
        raise DuplicateDocumentError(
            f"Ce document existe dÃ©jÃ  : {filename}"
        )

    pages = extract_pages(data, filename)
    drafts = chunk_pages(
        pages,
        chunk_size=settings.chunk_size,
        overlap=settings.chunk_overlap,
    )

    if not drafts:
        raise UnreadableDocumentError(
            "Aucun chunk exploitable n'a Ã©tÃ© gÃ©nÃ©rÃ©."
        )

    if embed_fn is None:
        from app.services.embeddings import embed_passages

        embed_fn = embed_passages

    document = Document(
        filename=filename,
        file_type=file_type,
        sha256=sha256,
        size_bytes=len(data),
        num_pages=len(pages) if file_type == "pdf" else None,
        num_chunks=0,
        status="processing",
        uploaded_by=uploaded_by,
    )

    try:
        db.add(document)
        db.flush()

        for start in range(0, len(drafts), 32):
            batch = drafts[start : start + 32]
            contents = [chunk.content for chunk in batch]

            embeddings = embed_fn(contents)

            if len(embeddings) != len(batch):
                raise ValueError(
                    "Le nombre de vecteurs ne correspond pas au nombre de chunks."
                )

            db_chunks = []

            for draft, embedding in zip(batch, embeddings, strict=True):
                if len(embedding) != settings.embedding_dim:
                    raise ValueError(
                        f"Dimension incorrecte : {len(embedding)}. "
                        f"Dimension attendue : {settings.embedding_dim}."
                    )

                db_chunks.append(
                    Chunk(
                        document_id=document.id,
                        chunk_index=draft.chunk_index,
                        page=draft.page,
                        content=draft.content,
                        embedding=embedding,
                    )
                )

            db.add_all(db_chunks)
            db.flush()

        document.num_chunks = len(drafts)
        document.status = "ready"

        db.commit()
        db.refresh(document)

        return document

    except Exception:
        db.rollback()

        failed_document = Document(
            filename=filename,
            file_type=file_type,
            sha256=sha256,
            size_bytes=len(data),
            num_pages=len(pages) if file_type == "pdf" else None,
            num_chunks=0,
            status="failed",
            uploaded_by=uploaded_by,
        )

        db.add(failed_document)
        db.commit()

        raise