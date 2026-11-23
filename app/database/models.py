"""
SQLAlchemy ORM models for structured metadata storage.
"""

from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Boolean, Integer,
    DateTime, Float, ForeignKey, ARRAY,
)
from sqlalchemy.orm import relationship
from app.database.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Paper(Base):
    __tablename__ = "papers"

    id = Column(String, primary_key=True, default=_uuid)
    pmid = Column(String, unique=True, nullable=True, index=True)
    doi = Column(String, unique=True, nullable=True, index=True)
    title = Column(Text, nullable=False)
    authors = Column(Text, nullable=True)        # JSON-encoded list
    year = Column(String, nullable=True)
    abstract = Column(Text, nullable=True)
    url = Column(String, nullable=True)
    source = Column(String, nullable=True)       # pubmed | semantic_scholar
    full_text_available = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship("PaperChunk", back_populates="paper", cascade="all, delete-orphan")
    evidence = relationship("Evidence", back_populates="paper", cascade="all, delete-orphan")


class PaperChunk(Base):
    __tablename__ = "paper_chunks"

    id = Column(String, primary_key=True, default=_uuid)
    chunk_id = Column(String, unique=True, nullable=False, index=True)
    paper_id = Column(String, ForeignKey("papers.id"), nullable=False)
    text = Column(Text, nullable=False)
    section = Column(String, nullable=True)
    page = Column(Integer, nullable=True)
    qdrant_point_id = Column(String, nullable=True)   # ID in the Qdrant collection
    created_at = Column(DateTime, default=datetime.utcnow)

    paper = relationship("Paper", back_populates="chunks")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String, primary_key=True, default=_uuid)
    paper_id = Column(String, ForeignKey("papers.id"), nullable=False)
    research_objective = Column(Text, nullable=True)
    dataset = Column(Text, nullable=True)
    sample_size = Column(String, nullable=True)
    methodology = Column(Text, nullable=True)
    evaluation_metrics = Column(Text, nullable=True)   # JSON list
    main_results = Column(Text, nullable=True)
    key_findings = Column(Text, nullable=True)
    limitations = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    paper = relationship("Paper", back_populates="evidence")


class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id = Column(String, primary_key=True, default=_uuid)
    question = Column(Text, nullable=False)
    report_json = Column(Text, nullable=True)   # serialized ResearchReport
    created_at = Column(DateTime, default=datetime.utcnow)
