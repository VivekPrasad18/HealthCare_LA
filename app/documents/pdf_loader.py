"""
PDF loading with PyMuPDF (fitz).
Returns raw per-page text with page numbers preserved.
"""

from __future__ import annotations
import io
from pathlib import Path
from typing import List, Tuple, Union

import pymupdf as fitz  # PyMuPDF (new import path)

from app.utils.logging import get_logger

logger = get_logger(__name__)

PageText = Tuple[int, str]   # (page_number_1_indexed, text)


def load_pdf_from_path(pdf_path: Union[str, Path]) -> List[PageText]:
    """Extract text from a PDF file on disk. Returns list of (page_no, text)."""
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages: List[PageText] = []
    with fitz.open(str(path)) as doc:
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text")
            if text.strip():
                pages.append((i, text))

    logger.info(f"Loaded {len(pages)} pages from {path.name}")
    return pages


def load_pdf_from_bytes(pdf_bytes: bytes, name: str = "document") -> List[PageText]:
    """Extract text from PDF content already in memory."""
    pages: List[PageText] = []
    with fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf") as doc:
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text")
            if text.strip():
                pages.append((i, text))

    logger.info(f"Loaded {len(pages)} pages from in-memory PDF '{name}'")
    return pages
