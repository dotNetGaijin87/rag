"""Text chunking — pure function, no dependencies.

Sliding window over whitespace-delimited tokens so words are never split mid-token.
"""

from __future__ import annotations


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split *text* into overlapping chunks of roughly *chunk_size* characters.

    The window advances by ``chunk_size - overlap`` characters each step and snaps to
    word boundaries so chunks never cut a word in half.
    """
    text = (text or "").strip()
    if not text:
        return []
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    words = text.split()
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for word in words:
        # +1 accounts for the joining space.
        addition = len(word) + (1 if current else 0)
        if current_len + addition > chunk_size and current:
            chunks.append(" ".join(current))
            # Build the overlap tail from the end of the current chunk.
            current, current_len = _overlap_tail(current, overlap)
        if current:
            current_len += len(word) + 1
        else:
            current_len += len(word)
        current.append(word)

    if current:
        chunks.append(" ".join(current))
    return chunks


def _overlap_tail(words: list[str], overlap: int) -> tuple[list[str], int]:
    """Return the trailing words of *words* whose combined length is <= *overlap*."""
    tail: list[str] = []
    length = 0
    for word in reversed(words):
        addition = len(word) + (1 if tail else 0)
        if length + addition > overlap:
            break
        tail.insert(0, word)
        length += addition
    return tail, length
