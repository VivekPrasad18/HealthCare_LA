"""
CRUD helpers for the relational database.
All vector operations live in app/rag/vector_store.py.
"""

from __future__ import annotations
import json
from typing import List, Optional
from sqlalchemy.orm import Session

from app.database.models import Paper, PaperChunk, Evidence, ResearchSession
from app.schemas.paper import PaperMetadata, PaperChunk as PaperChunkSchema
from app.schemas.evidence import ExtractedEvidence
from app.schemas.research import ResearchReport
from app.utils.logging import get_logger

logger = get_logger(__name__)


# ── Paper ───────────────────────────────────────────────────────────────────

def upsert_paper(db: Session, meta: PaperMetadata) -> Paper:
    """Insert or update a paper record. Deduplicates by DOI then PMID."""
    existing = None
    if meta.doi:
        existing = db.query(Paper).filter(Paper.doi == meta.doi).first()
    if not existing and meta.pmid:
        existing = db.query(Paper).filter(Paper.pmid == meta.pmid).first()

    if existing:
        return existing

    paper = Paper(
        pmid=meta.pmid,
        doi=meta.doi,
        title=meta.title,
        authors=json.dumps(meta.authors),
        year=meta.year,
        abstract=meta.abstract,
        url=meta.url,
        source=meta.source,
        full_text_available=meta.full_text_available,
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)
    logger.info(f"Stored paper: {paper.title[:60]}...")
    return paper


def get_all_papers(db: Session) -> List[Paper]:
    return db.query(Paper).all()


# ── Chunks ───────────────────────────────────────────────────────────────────

def store_chunk(db: Session, chunk: PaperChunkSchema, db_paper_id: str) -> PaperChunk:
    existing = db.query(PaperChunk).filter(PaperChunk.chunk_id == chunk.chunk_id).first()
    if existing:
        return existing

    db_chunk = PaperChunk(
        chunk_id=chunk.chunk_id,
        paper_id=db_paper_id,
        text=chunk.text,
        section=chunk.section,
        page=chunk.page,
    )
    db.add(db_chunk)
    db.commit()
    db.refresh(db_chunk)
    return db_chunk


def update_chunk_qdrant_id(db: Session, chunk_id: str, qdrant_point_id: str):
    chunk = db.query(PaperChunk).filter(PaperChunk.chunk_id == chunk_id).first()
    if chunk:
        chunk.qdrant_point_id = qdrant_point_id
        db.commit()


# ── Evidence ─────────────────────────────────────────────────────────────────

def store_evidence(db: Session, ev: ExtractedEvidence, db_paper_id: str) -> Evidence:
    db_ev = Evidence(
        paper_id=db_paper_id,
        research_objective=ev.research_objective,
        dataset=ev.dataset,
        sample_size=ev.sample_size,
        methodology=ev.methodology,
        evaluation_metrics=json.dumps(ev.evaluation_metrics),
        main_results=ev.main_results,
        key_findings=ev.key_findings,
        limitations=ev.limitations,
    )
    db.add(db_ev)
    db.commit()
    db.refresh(db_ev)
    return db_ev


# ── Research sessions ─────────────────────────────────────────────────────────

def create_session(db: Session, question: str) -> ResearchSession:
    session = ResearchSession(question=question)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def save_report(db: Session, session_id: str, report: ResearchReport):
    session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
    if session:
        session.report_json = report.model_dump_json()
        db.commit()


def get_session(db: Session, session_id: str) -> Optional[ResearchSession]:
    return db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
