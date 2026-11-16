
import pytest

from app.services.chunking import chunk_pages, chunk_text
from app.services.types import PageText


def test_empty_text_returns_empty_list():
    assert chunk_text("", chunk_size=20, overlap=5) == []


def test_whitespace_text_returns_empty_list():
    assert chunk_text("   \n  ", chunk_size=20, overlap=5) == []


def test_short_text_returns_one_chunk():
    text = "Hello university students."
    assert chunk_text(text, chunk_size=100, overlap=10) == [text]


def test_long_text_is_split():
    text = "First sentence is here. Second sentence is here."
    chunks = chunk_text(text, chunk_size=25, overlap=5)

    assert len(chunks) > 1


def test_chunks_respect_maximum_size():
    text = "One two three four five six seven eight nine ten."
    chunks = chunk_text(text, chunk_size=15, overlap=3)

    assert all(len(chunk) <= 15 for chunk in chunks)


def test_words_are_not_split():
    text = "University students study artificial intelligence."
    chunks = chunk_text(text, chunk_size=20, overlap=5)

    original_words = set(text.split())
    chunk_words = {
        word
        for chunk in chunks
        for word in chunk.split()
    }

    assert chunk_words.issubset(original_words)


def test_overlap_reuses_previous_words():
    text = "First sentence. Second sentence. Third sentence."
    chunks = chunk_text(text, chunk_size=20, overlap=8)

    assert len(chunks) >= 2
    assert any(
        set(previous.split()) & set(current.split())
        for previous, current in zip(chunks, chunks[1:], strict=True)
    )


def test_overlap_must_be_smaller_than_chunk_size():
    with pytest.raises(ValueError):
        chunk_text("Some text here.", chunk_size=10, overlap=10)


def test_chunk_size_must_be_positive():
    with pytest.raises(ValueError):
        chunk_text("Some text here.", chunk_size=0, overlap=0)


def test_chunk_pages_preserves_page_numbers_and_indexes():
    pages = [
        PageText(page=1, text="First page contains some text."),
        PageText(page=2, text="Second page contains other text."),
    ]

    chunks = chunk_pages(pages, chunk_size=20, overlap=5)

    assert len(chunks) > 0
    assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))
    assert all(chunk.page == 1 for chunk in chunks if "First" in chunk.content)
    assert all(chunk.page == 2 for chunk in chunks if "Second" in chunk.content)
