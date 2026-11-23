"""
Pydantic schemas for a retrieved scientific paper.
Used across literature retrieval, RAG ingestion, and database storage.
"""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class PaperMetadata(BaseModel):
    """Lightweight paper record returned by literature search."""

    pmid: Optional[str] = None
    doi: Optional[str] = None
    title: str
    authors: List[str] = Field(default_factory=list)
    year: Optional[str] = None
    abstract: Optional[str] = None
    url: Optional[str] = None
    source: str = "unknown"          # "pubmed" | "semantic_scholar"
    full_text_available: bool = False


class PaperChunk(BaseModel):
    """A single text chunk derived from a paper, ready for embedding."""

    chunk_id: str                    # "{paper_id}_chunk_{n}"
    paper_id: str                    # pmid or doi or generated id
    text: str
    section: Optional[str] = None   # "abstract" | "introduction" | "methods" | ...
    page: Optional[int] = None
    metadata: PaperMetadata
