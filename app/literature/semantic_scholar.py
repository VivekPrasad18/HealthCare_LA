"""
Semantic Scholar API integration.
Docs: https://api.semanticscholar.org/api-docs/
Free tier: 100 req/5 min unauthenticated; 1 req/sec with key.
"""

from __future__ import annotations
import time
from typing import Any, Dict, List, Optional

import requests

from app.utils.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

BASE_URL = "https://api.semanticscholar.org/graph/v1"
FIELDS = "paperId,externalIds,title,authors,year,abstract,openAccessPdf,publicationTypes"
HEADERS: Dict[str, str] = {}
if settings.SEMANTIC_SCHOLAR_API_KEY:
    HEADERS["x-api-key"] = settings.SEMANTIC_SCHOLAR_API_KEY


def search_semantic_scholar(
    query: str,
    max_results: int = 5,
    fields_of_study: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Search for papers matching *query*.
    Returns raw API records (not normalised yet).
    """
    params: Dict[str, Any] = {
        "query": query,
        "limit": min(max_results, 100),
        "fields": FIELDS,
    }
    if fields_of_study:
        params["fieldsOfStudy"] = ",".join(fields_of_study)

    try:
        resp = requests.get(
            f"{BASE_URL}/paper/search",
            params=params,
            headers=HEADERS,
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("data", [])
    except requests.RequestException as exc:
        logger.error(f"Semantic Scholar search failed: {exc}")
        return []


def fetch_paper(paper_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a single paper by its Semantic Scholar paperId or DOI (prefix 'DOI:')."""
    try:
        resp = requests.get(
            f"{BASE_URL}/paper/{paper_id}",
            params={"fields": FIELDS},
            headers=HEADERS,
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        logger.error(f"Semantic Scholar fetch failed for {paper_id}: {exc}")
        return None


def _normalise(record: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a Semantic Scholar record to the shared paper dict shape."""
    external = record.get("externalIds") or {}
    authors = [a.get("name", "") for a in (record.get("authors") or [])]
    pdf_info = record.get("openAccessPdf") or {}
    return {
        "pmid": external.get("PubMed"),
        "doi": external.get("DOI"),
        "title": record.get("title") or "Unknown title",
        "authors": authors,
        "year": str(record.get("year")) if record.get("year") else None,
        "abstract": record.get("abstract"),
        "url": pdf_info.get("url") or f"https://www.semanticscholar.org/paper/{record.get('paperId', '')}",
        "source": "semantic_scholar",
        "full_text_available": bool(pdf_info.get("url")),
        "_ss_paper_id": record.get("paperId"),
    }


def query_semantic_scholar(
    query: str,
    max_results: int = 5,
) -> List[Dict[str, Any]]:
    """Complete pipeline: search → normalise. Returns list of normalised paper dicts."""
    raw = search_semantic_scholar(query, max_results)
    time.sleep(0.5)   # be polite to the free tier
    return [_normalise(r) for r in raw]
