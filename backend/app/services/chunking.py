import re

from app.services.types import ChunkDraft, PageText


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    if not text or not text.strip():
        return []

    paragraphs = re.split(r"\n\s*\n", text.strip())
    units = []

    for paragraph in paragraphs:
        paragraph = re.sub(r"\s+", " ", paragraph).strip()

        if not paragraph:
            continue

        if len(paragraph) <= chunk_size:
            units.append(paragraph)
            continue

        sentences = re.split(r"(?<=[.!?])\s+", paragraph)

        for sentence in sentences:
            sentence = sentence.strip()

            if not sentence:
                continue

            if len(sentence) <= chunk_size:
                units.append(sentence)
                continue

            for word in sentence.split():
                if len(word) > chunk_size:
                    raise ValueError(
                        f"A word exceeds chunk_size ({chunk_size} characters)"
                    )
                units.append(word)

    chunks = []
    current = ""

    for unit in units:
        candidate = f"{current} {unit}".strip() if current else unit

        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)

        overlap_words = []
        overlap_length = 0

        if overlap > 0:
            for word in reversed(current.split()):
                extra_length = len(word) + (1 if overlap_words else 0)

                if overlap_length + extra_length > overlap:
                    break

                overlap_words.insert(0, word)
                overlap_length += extra_length

        current = " ".join(overlap_words)

        while current and len(f"{current} {unit}") > chunk_size:
            overlap_words.pop(0)
            current = " ".join(overlap_words)

        current = f"{current} {unit}".strip()

    if current:
        chunks.append(current)

    return [chunk for chunk in chunks if chunk]


def chunk_pages(
    pages: list[PageText],
    chunk_size: int,
    overlap: int,
) -> list[ChunkDraft]:
    chunks = []
    chunk_index = 0

    for page in pages:
        page_chunks = chunk_text(page.text, chunk_size, overlap)

        for content in page_chunks:
            chunks.append(
                ChunkDraft(
                    chunk_index=chunk_index,
                    page=page.page,
                    content=content,
                )
            )
            chunk_index += 1

    return chunks
