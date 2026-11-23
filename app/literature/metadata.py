"""
Metadata normalisation and deduplication across literature sources.
Both PubMed and Semantic Scholar produce dicts with the same keys after their
respective normalisation steps; this module merges them into PaperMetadata objects.
"""

from __future__ import annotations
from typing import Any, Dict, List

from app.schemas.paper import PaperMetadata
from app.utils.logging import get_logger

logger = get_logger(__name__)


def to_paper_metadata(raw: Dict[str, Any]) -> PaperMetadata:
    """Convert a normalised source dict to a PaperMetadata Pydantic model."""
    return PaperMetadata(
        pmid=raw.get("pmid"),
        doi=raw.get("doi"),
        title=raw.get("title") or "Unknown title",
        authors=raw.get("authors") or [],
        year=raw.get("year"),
        abstract=raw.get("abstract"),
        url=raw.get("url"),
        source=raw.get("source", "unknown"),
        full_text_available=raw.get("full_text_available", False),
    )


def deduplicate(papers: List[PaperMetadata]) -> List[PaperMetadata]:
    """
    Remove duplicate papers by DOI first, then by PMID.
    Papers without either identifier are kept.
    """
    seen_doi: set = set()
    seen_pmid: set = set()
    unique: List[PaperMetadata] = []

    for p in papers:
        if p.doi and p.doi in seen_doi:
            continue
        if p.pmid and p.pmid in seen_pmid:
            continue
        unique.append(p)
        if p.doi:
            seen_doi.add(p.doi)
        if p.pmid:
            seen_pmid.add(p.pmid)

    removed = len(papers) - len(unique)
    if removed:
        logger.info(f"Deduplication removed {removed} duplicate paper(s).")
    return unique


def merge_sources(*source_lists: List[Dict[str, Any]]) -> List[PaperMetadata]:
    """
    Accept N lists of raw paper dicts (from different sources),
    convert to PaperMetadata, and deduplicate.
    """
    all_raw: List[Dict[str, Any]] = []
    for lst in source_lists:
        all_raw.extend(lst)
    papers = [to_paper_metadata(r) for r in all_raw]
    return deduplicate(papers)
