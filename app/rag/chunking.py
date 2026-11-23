"""
Fixed-size text chunking with overlap.
Splits on sentence boundaries where possible to avoid cutting mid-sentence.
"""

from __future__ import annotations
import re
from typing import List

from app.utils.config import settings


def _split_sentences(text: str) -> List[str]:
    """Rough sentence splitter that handles common abbreviations."""
    return re.split(r"(?<=[.!?])\s+", text.strip())


def chunk_text(
    text: str,
    chunk_size: int = settings.CHUNK_SIZE,
    overlap: int = settings.CHUNK_OVERLAP,
) -> List[str]:
    """
    Split *text* into overlapping chunks of approximately *chunk_size* characters.

    Strategy:
      1. Split into sentences.
      2. Accumulate sentences until the chunk would exceed chunk_size.
      3. Start a new chunk, re-including the last *overlap* characters worth
         of sentences (approximated by keeping the last sentence or two).
    """
    if not text or not text.strip():
        return []

    sentences = _split_sentences(text)
    chunks: List[str] = []
    current: List[str] = []
    current_len = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        slen = len(sentence) + 1  # +1 for the space

        if current_len + slen > chunk_size and current:
            chunk = " ".join(current).strip()
            chunks.append(chunk)

            # Carry over sentences that fit within the overlap window
            overlap_buf: List[str] = []
            overlap_len = 0
            for s in reversed(current):
                if overlap_len + len(s) + 1 <= overlap:
                    overlap_buf.insert(0, s)
                    overlap_len += len(s) + 1
                else:
                    break
            current = overlap_buf
            current_len = overlap_len

        current.append(sentence)
        current_len += slen

    if current:
        chunks.append(" ".join(current).strip())

    # Safety: if a single sentence exceeds chunk_size, hard-split it
    final: List[str] = []
    for c in chunks:
        if len(c) <= chunk_size * 1.5:
            final.append(c)
        else:
            # Hard split
            for i in range(0, len(c), chunk_size):
                final.append(c[i : i + chunk_size])

    return final
