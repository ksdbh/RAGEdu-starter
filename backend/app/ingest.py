# backend/app/ingest.py
from __future__ import annotations

from typing import List


def semantic_chunk_text(text: str, max_chars: int = 800, overlap: int = 100) -> List[str]:
    """
    Split raw text into overlapping, sentence-aware chunks.

    - Breaks on blank-line separated paragraphs first.
    - Within each paragraph, emits chunks up to `max_chars`.
    - Tries to end chunks at a sentence boundary ('.') when possible.
    - Overlaps chunks by `overlap` characters to preserve context.

    Returns a list of chunk strings. Empty/whitespace-only input -> [].
    """
    if not text or not text.strip():
        return []

    # Normalize newlines and split paragraphs
    normalized = text.replace("\r\n", "\n")
    paragraphs = [p.strip() for p in normalized.split("\n\n") if p.strip()]
    chunks: List[str] = []

    for p in paragraphs:
        start = 0
        plen = len(p)

        while start < plen:
            end = min(start + max_chars, plen)

            # Try to cut on a sentence boundary inside [start, end]
            cut = p.rfind(".", start, end)
            # Only cut at '.' if it's not too close to start, to avoid tiny chunks
            if cut != -1 and cut > start + min(80, max_chars // 4):
                end = cut + 1  # include the period

            piece = p[start:end].strip()
            if piece:
                chunks.append(piece)

            # advance with overlap (but never go backwards)
            if end >= plen:
                break
            start = max(end - overlap, end)

    return chunks