"""
Qdrant vector store operations.
Handles collection creation, upsert, and search.
"""

from __future__ import annotations
import uuid
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    PointStruct,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue,
)

from app.utils.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

_client: Optional[QdrantClient] = None


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        try:
            # Try connecting to a running Qdrant server first
            client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=3)
            client.get_collections()   # quick ping
            _client = client
            logger.info(f"Connected to Qdrant server at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
        except Exception:
            # Fall back to in-memory Qdrant (no Docker needed)
            _client = QdrantClient(":memory:")
            logger.info("Qdrant server not reachable — using in-memory mode (data lost on restart)")
    return _client


def ensure_collection(dim: Optional[int] = None):
    """Create the Qdrant collection if it doesn't already exist.
    If it exists with a different dimension, recreate it."""
    client = get_client()
    dim = dim or settings.EMBEDDING_DIM
    existing = [c.name for c in client.get_collections().collections]

    if settings.QDRANT_COLLECTION in existing:
        # Check dimension matches
        try:
            info = client.get_collection(settings.QDRANT_COLLECTION)
            existing_dim = info.config.params.vectors.size
            if existing_dim != dim:
                logger.warning(f"Collection dim mismatch ({existing_dim} vs {dim}) — recreating.")
                client.delete_collection(settings.QDRANT_COLLECTION)
            else:
                logger.debug(f"Qdrant collection '{settings.QDRANT_COLLECTION}' already exists (dim={dim}).")
                return
        except Exception:
            pass  # can't check — proceed to create

    client.create_collection(
        collection_name=settings.QDRANT_COLLECTION,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )
    logger.info(f"Created Qdrant collection '{settings.QDRANT_COLLECTION}' (dim={dim})")


def upsert_vectors(
    vectors: List[List[float]],
    payloads: List[Dict[str, Any]],
    ids: Optional[List[str]] = None,
) -> List[str]:
    """
    Upsert vectors with their metadata payloads.
    Point IDs must be valid UUIDs — chunk_id is stored in the payload instead.
    Returns the list of UUID point IDs used.
    """
    ensure_collection(len(vectors[0]) if vectors else None)
    client = get_client()

    # Always generate proper UUIDs for Qdrant point IDs
    point_ids = [str(uuid.uuid4()) for _ in vectors]

    points = [
        PointStruct(id=point_id, vector=vec, payload=payload)
        for point_id, vec, payload in zip(point_ids, vectors, payloads)
    ]
    client.upsert(collection_name=settings.QDRANT_COLLECTION, points=points)
    logger.info(f"Upserted {len(points)} vectors into Qdrant.")
    return point_ids


def search_vectors(
    query_vector: List[float],
    top_k: int = settings.RETRIEVAL_TOP_K,
    filter_paper_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Semantic search using query_points (qdrant-client >= 1.7).
    Optionally filter by paper_id payload field.
    Returns list of {score, chunk_id, text, section, paper_id, ...} dicts.
    """
    client = get_client()

    qdrant_filter = None
    if filter_paper_id:
        qdrant_filter = Filter(
            must=[FieldCondition(key="paper_id", match=MatchValue(value=filter_paper_id))]
        )

    response = client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        limit=top_k,
        query_filter=qdrant_filter,
        with_payload=True,
    )

    results = []
    for hit in response.points:
        payload = hit.payload or {}
        results.append(
            {
                "score": hit.score,
                "chunk_id": payload.get("chunk_id"),
                "text": payload.get("text"),
                "section": payload.get("section"),
                "paper_id": payload.get("paper_id"),
                "title": payload.get("title"),
                "authors": payload.get("authors"),
                "year": payload.get("year"),
                "url": payload.get("url"),
            }
        )
    return results
