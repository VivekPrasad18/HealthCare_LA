"""
High-level document processor: takes a PaperMetadata + optional PDF bytes/path
and produces a list of PaperChunk objects ready for embedding.

If no PDF is available, the abstract is used as a single chunk.
"""

from __future__ import annotations
import hashlib
from pathlib import Path
from typing import List, Optional, Union

from app.documents.pdf_loader import load_pdf_from_bytes, load_pdf_from_path
from app.documents.parser import parse_pages
from app.rag.chunking import chunk_text
from app.schemas.paper import PaperChunk, PaperMetadata
from app.utils.logging import get_logger

logger = get_logger(__name__)


def _make_chunk_id(paper_id: str, section: str, index: int) -> str:
    raw = f"{paper_id}_{section}_{index}"
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def _paper_id(meta: PaperMetadata) -> str:
    return meta.doi or meta.pmid or hashlib.md5(meta.title.encode()).hexdigest()[:12]


def process_pdf(
    meta: PaperMetadata,
    pdf_source: Union[bytes, str, Path],
) -> List[PaperChunk]:
    """Process a PDF (bytes or path) into labelled, chunked PaperChunk objects."""
    if isinstance(pdf_source, bytes):
        pages = load_pdf_from_bytes(pdf_source, name=meta.title[:40])
    else:
        pages = load_pdf_from_path(pdf_source)

    section_blocks = parse_pages(pages)
    paper_id = _paper_id(meta)
    chunks: List[PaperChunk] = []

    for section_label, page_no, text in section_blocks:
        # Skip references section — not useful for RAG
        if section_label == "references":
            continue
        for idx, chunk_text_piece in enumerate(chunk_text(text)):
            chunk_id = _make_chunk_id(paper_id, section_label, idx)
            chunks.append(
                PaperChunk(
                    chunk_id=chunk_id,
                    paper_id=paper_id,
                    text=chunk_text_piece,
                    section=section_label,
                    page=page_no,
                    metadata=meta,
                )
            )

    logger.info(f"Produced {len(chunks)} chunks from PDF: {meta.title[:50]}")
    return chunks


def process_abstract(meta: PaperMetadata) -> List[PaperChunk]:
    """
    Fallback: create chunks from the abstract when no PDF is available.
    Usually results in 1–2 chunks.
    """
    if not meta.abstract:
        logger.warning(f"No abstract available for paper: {meta.title[:50]}")
        return []

    paper_id = _paper_id(meta)
    chunks: List[PaperChunk] = []
    for idx, piece in enumerate(chunk_text(meta.abstract)):
        chunk_id = _make_chunk_id(paper_id, "abstract", idx)
        chunks.append(
            PaperChunk(
                chunk_id=chunk_id,
                paper_id=paper_id,
                text=piece,
                section="abstract",
                page=None,
                metadata=meta,
            )
        )
    return chunks


def process_paper(
    meta: PaperMetadata,
    pdf_source: Optional[Union[bytes, str, Path]] = None,
) -> List[PaperChunk]:
    """
    Entry point: use PDF if provided, otherwise fall back to abstract.
    """
    if pdf_source is not None:
        try:
            return process_pdf(meta, pdf_source)
        except Exception as exc:
            logger.warning(f"PDF processing failed ({exc}), falling back to abstract.")
    return process_abstract(meta)
