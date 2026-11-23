"""
RAG ingestion pipeline: takes PaperChunk objects and indexes them into Qdrant
(and optionally into the relational DB).

Usage:
    from app.rag.pipeline import ingest_chunks
    ingest_chunks(chunks, db_session)
"""

from __future__ import annotations
from typing import List, Optional

from sqlalchemy.orm import Session

from app.rag.embeddings import embed_texts
from app.rag.vector_store import upsert_vectors
from app.database import crud
from app.schemas.paper import PaperChunk
from app.utils.logging import get_logger

logger = get_logger(__name__)


def ingest_chunks(
    chunks: List[PaperChunk],
    db: Optional[Session] = None,
) -> int:
    """
    Embed all chunks and upsert them into Qdrant.
    If a DB session is provided, also stores chunk records relationally.

    Returns the number of chunks successfully ingested.
    """
    if not chunks:
        return 0

    texts = [c.text for c in chunks]
    logger.info(f"Embedding {len(texts)} chunks...")
    vectors = embed_texts(texts)

    payloads = []
    for chunk in chunks:
        m = chunk.metadata
        payloads.append(
            {
                "chunk_id": chunk.chunk_id,
                "paper_id": chunk.paper_id,
                "text": chunk.text,
                "section": chunk.section,
                "page": chunk.page,
                "title": m.title,
                "authors": m.authors,
                "year": m.year,
                "doi": m.doi,
                "pmid": m.pmid,
                "url": m.url,
                "source": m.source,
            }
        )

    ids = [c.chunk_id for c in chunks]
    upserted_ids = upsert_vectors(vectors, payloads, ids=ids)

    if db is not None:
        for chunk, qdrant_id in zip(chunks, upserted_ids):
            # Ensure parent paper exists
            db_paper = crud.upsert_paper(db, chunk.metadata)
            db_chunk = crud.store_chunk(db, chunk, db_paper.id)
            crud.update_chunk_qdrant_id(db, db_chunk.chunk_id, qdrant_id)

    logger.info(f"Ingested {len(chunks)} chunks into Qdrant.")
    return len(chunks)


def ingest_paper(
    meta,              # PaperMetadata
    pdf_source=None,   # bytes | str | Path | None
    db: Optional[Session] = None,
) -> int:
    """
    Convenience wrapper: process a paper (PDF or abstract) and ingest it.
    Returns number of chunks produced and ingested.
    """
    from app.documents.processor import process_paper

    chunks = process_paper(meta, pdf_source)
    if not chunks:
        logger.warning(f"No chunks produced for: {meta.title[:50]}")
        return 0

    if db is not None:
        crud.upsert_paper(db, meta)

    return ingest_chunks(chunks, db)
