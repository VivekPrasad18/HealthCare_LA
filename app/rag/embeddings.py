"""
Embedding generation.
Supports sentence-transformers (default) and OpenAI embeddings.
The embedding model is loaded once and reused (singleton pattern).
"""

from __future__ import annotations
from typing import List

from app.utils.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

_model = None   # lazy-loaded singleton


def _load_model():
    global _model
    if _model is not None:
        return _model

    provider = settings.EMBEDDING_PROVIDER

    if provider == "sentence_transformers":
        from sentence_transformers import SentenceTransformer
        logger.info(f"Loading sentence-transformers model: {settings.EMBEDDING_MODEL}")
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)

    elif provider == "openai":
        import openai
        openai.api_key = settings.OPENAI_API_KEY
        # Wrap into a duck-typed object so callers use the same interface
        class _OpenAIWrapper:
            def encode(self, texts: List[str]) -> List[List[float]]:
                resp = openai.embeddings.create(
                    model=settings.EMBEDDING_MODEL or "text-embedding-3-small",
                    input=texts,
                )
                return [item.embedding for item in resp.data]
        _model = _OpenAIWrapper()
        logger.info("Using OpenAI embeddings.")

    else:
        raise ValueError(f"Unknown EMBEDDING_PROVIDER: {provider}")

    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Embed a list of strings. Returns a list of float vectors.
    Batching is handled internally by the model.
    """
    if not texts:
        return []
    model = _load_model()
    vectors = model.encode(texts)
    # sentence-transformers returns numpy arrays; convert to plain lists
    if hasattr(vectors, "tolist"):
        return vectors.tolist()
    return list(vectors)


def embed_query(query: str) -> List[float]:
    """Embed a single query string."""
    return embed_texts([query])[0]
