"""
RAG retriever: embeds a query and returns the top-k relevant chunks.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from app.rag.embeddings import embed_query
from app.rag.vector_store import search_vectors
from app.utils.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


def retrieve(
    query: str,
    top_k: int = settings.RETRIEVAL_TOP_K,
    filter_paper_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Embed *query*, search Qdrant, and return the top-k matching chunks.

    Each result dict contains:
        score, chunk_id, text, section, paper_id, title, authors, year, url
    """
    logger.debug(f"Retrieving top-{top_k} chunks for: {query[:80]}")
    q_vec = embed_query(query)
    results = search_vectors(q_vec, top_k=top_k, filter_paper_id=filter_paper_id)
    logger.debug(f"Retrieved {len(results)} chunks.")
    return results


def build_context(chunks: List[Dict[str, Any]], max_tokens: int = 3000) -> str:
    """
    Concatenate chunk texts into a single context string for the LLM.
    Respects a rough character budget (1 token ≈ 4 chars).
    Each chunk is prefixed with its source citation.
    """
    char_budget = max_tokens * 4
    parts: List[str] = []
    used = 0

    for c in chunks:
        title = c.get("title") or "Unknown"
        year = c.get("year") or "n.d."
        section = c.get("section") or "text"
        text = c.get("text") or ""
        snippet = f"[Source: {title} ({year}), section: {section}]\n{text}"
        if used + len(snippet) > char_budget:
            break
        parts.append(snippet)
        used += len(snippet)

    return "\n\n---\n\n".join(parts)
