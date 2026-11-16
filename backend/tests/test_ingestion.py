
import hashlib
import uuid

import pymupdf
import pytest
from sqlalchemy import func, select

from app.core.config import get_settings
from app.db.models import Chunk, Document
from app.db.session import SessionLocal
from app.services.ingestion import (
    DuplicateDocumentError,
    UnreadableDocumentError,
    extract_pages,
    ingest_document,
)


def unique_text(prefix="ingestion test"):
    return f"{prefix} {uuid.uuid4()}"


def fake_embeddings(texts):
    dimension = get_settings().embedding_dim
    return [[0.0] * dimension for _ in texts]


def create_pdf(text=None):
    pdf = pymupdf.open()
    page = pdf.new_page()

    if text:
        page.insert_text((72, 72), text)

    data = pdf.tobytes()
    pdf.close()
    return data


def cleanup_document(db, data):
    sha256 = hashlib.sha256(data).hexdigest()

    document = db.scalar(
        select(Document).where(Document.sha256 == sha256)
    )

    if document is not None:
        db.delete(document)
        db.commit()


def test_extract_txt():
    text = unique_text()
    pages = extract_pages(text.encode("utf-8"), "test.txt")

    assert len(pages) == 1
    assert pages[0].page is None
    assert pages[0].text == text


def test_extract_txt_latin1_fallback():
    pages = extract_pages(b"caf\xe9", "test.txt")

    assert pages[0].text == "café"


def test_extract_pdf():
    data = create_pdf(unique_text("PDF test"))
    pages = extract_pages(data, "test.pdf")

    assert len(pages) == 1
    assert pages[0].page == 1
    assert "PDF test" in pages[0].text


def test_empty_file_is_rejected():
    with pytest.raises(UnreadableDocumentError):
        extract_pages(b"", "empty.txt")


def test_blank_txt_is_rejected():
    with pytest.raises(UnreadableDocumentError):
        extract_pages(b"   \n  ", "blank.txt")


def test_unsupported_format_is_rejected():
    with pytest.raises(UnreadableDocumentError):
        extract_pages(b"Some content", "document.docx")


def test_blank_pdf_is_rejected():
    data = create_pdf()

    with pytest.raises(UnreadableDocumentError):
        extract_pages(data, "blank.pdf")


def test_invalid_pdf_is_rejected():
    with pytest.raises(UnreadableDocumentError):
        extract_pages(b"not a valid PDF", "invalid.pdf")


def test_ingest_txt_success():
    data = unique_text("Successful TXT ingestion").encode("utf-8")
    db = SessionLocal()

    try:
        document = ingest_document(
            db,
            data,
            "success_test.txt",
            None,
            fake_embeddings,
        )

        assert document.status == "ready"
        assert document.num_chunks > 0
        assert document.num_pages is None

        actual_chunks = db.scalar(
            select(func.count())
            .select_from(Chunk)
            .where(Chunk.document_id == document.id)
        )

        assert actual_chunks == document.num_chunks

    finally:
        cleanup_document(db, data)
        db.close()


def test_ingest_pdf_success():
    data = create_pdf(unique_text("Successful PDF ingestion"))
    db = SessionLocal()

    try:
        document = ingest_document(
            db,
            data,
            "success_test.pdf",
            None,
            fake_embeddings,
        )

        assert document.status == "ready"
        assert document.num_pages == 1
        assert document.num_chunks > 0

    finally:
        cleanup_document(db, data)
        db.close()


def test_duplicate_document_is_rejected():
    data = unique_text("Duplicate ingestion test").encode("utf-8")
    db = SessionLocal()

    try:
        first = ingest_document(
            db, data, "first.txt", None, fake_embeddings
        )

        assert first.status == "ready"

        with pytest.raises(DuplicateDocumentError):
            ingest_document(
                db, data, "second.txt", None, fake_embeddings
            )

    finally:
        cleanup_document(db, data)
        db.close()


def test_embedding_error_creates_failed_document_without_chunks():
    data = unique_text("Embedding failure test").encode("utf-8")
    db = SessionLocal()

    def failing_embeddings(texts):
        raise RuntimeError("Simulated embedding failure")

    try:
        with pytest.raises(
            RuntimeError, match="Simulated embedding failure"
        ):
            ingest_document(
                db,
                data,
                "failed_test.txt",
                None,
                failing_embeddings,
            )

        sha256 = hashlib.sha256(data).hexdigest()

        document = db.scalar(
            select(Document).where(Document.sha256 == sha256)
        )

        assert document is not None
        assert document.status == "failed"
        assert document.num_chunks == 0

        actual_chunks = db.scalar(
            select(func.count())
            .select_from(Chunk)
            .where(Chunk.document_id == document.id)
        )

        assert actual_chunks == 0

    finally:
        cleanup_document(db, data)
        db.close()


def test_wrong_embedding_dimension_is_rejected():
    data = unique_text("Wrong embedding dimension").encode("utf-8")
    db = SessionLocal()

    def wrong_embeddings(texts):
        return [[0.0] * 10 for _ in texts]

    try:
        with pytest.raises(ValueError, match="Dimension incorrecte"):
            ingest_document(
                db,
                data,
                "wrong_dimension.txt",
                None,
                wrong_embeddings,
            )

        sha256 = hashlib.sha256(data).hexdigest()
        document = db.scalar(
            select(Document).where(Document.sha256 == sha256)
        )

        assert document is not None
        assert document.status == "failed"
        assert document.num_chunks == 0

    finally:
        cleanup_document(db, data)
        db.close()


def test_wrong_number_of_embeddings_is_rejected():
    data = unique_text("Wrong embedding count").encode("utf-8")
    db = SessionLocal()

    def wrong_count_embeddings(texts):
        return []

    try:
        with pytest.raises(ValueError, match="nombre de vecteurs"):
            ingest_document(
                db,
                data,
                "wrong_count.txt",
                None,
                wrong_count_embeddings,
            )

        sha256 = hashlib.sha256(data).hexdigest()
        document = db.scalar(
            select(Document).where(Document.sha256 == sha256)
        )

        assert document is not None
        assert document.status == "failed"
        assert document.num_chunks == 0

    finally:
        cleanup_document(db, data)
        db.close()
