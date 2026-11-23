"""
Pydantic schemas for evidence extraction and validation.
"""

from __future__ import annotations
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ValidationStatus(str, Enum):
    SUPPORTED = "supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    UNSUPPORTED = "unsupported"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class ExtractedEvidence(BaseModel):
    """Structured information extracted from a single paper."""

    paper_id: str
    title: str
    research_objective: Optional[str] = None
    dataset: Optional[str] = None
    sample_size: Optional[str] = None
    methodology: Optional[str] = None
    evaluation_metrics: List[str] = Field(default_factory=list)
    main_results: Optional[str] = None
    key_findings: Optional[str] = None
    limitations: Optional[str] = None


class ValidatedClaim(BaseModel):
    """A generated claim mapped to its supporting source passage."""

    claim: str
    source_paper_id: Optional[str] = None
    source_chunk_id: Optional[str] = None
    source_passage: Optional[str] = None
    validation_status: ValidationStatus = ValidationStatus.INSUFFICIENT_EVIDENCE
    confidence: float = 0.0          # 0.0 – 1.0


class ResearchGap(BaseModel):
    """A research gap identified from the analyzed literature."""

    gap_description: str
    supporting_paper_ids: List[str] = Field(default_factory=list)
    gap_type: str = "general"        # "dataset" | "methodology" | "population" | "reproducibility" | ...
