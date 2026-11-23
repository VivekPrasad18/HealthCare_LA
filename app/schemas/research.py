"""
Pydantic schemas for research requests, agent state, and final reports.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.paper import PaperMetadata
from app.schemas.evidence import ExtractedEvidence, ValidatedClaim, ResearchGap


# ── API request / response ──────────────────────────────────────────────────

class ResearchRequest(BaseModel):
    question: str = Field(..., min_length=10, description="Healthcare research question")
    max_papers: int = Field(default=10, ge=1, le=50)
    sources: List[str] = Field(default=["pubmed", "semantic_scholar"])


class ResearchResponse(BaseModel):
    question: str
    report: "ResearchReport"
    session_id: str


# ── Agent workflow state ────────────────────────────────────────────────────

class AgentState(BaseModel):
    """Shared mutable state passed between LangGraph nodes."""

    question: str
    sub_questions: List[str] = Field(default_factory=list)
    search_queries: List[str] = Field(default_factory=list)
    retrieved_papers: List[PaperMetadata] = Field(default_factory=list)
    extracted_evidence: List[ExtractedEvidence] = Field(default_factory=list)
    validated_claims: List[ValidatedClaim] = Field(default_factory=list)
    synthesis: Optional[str] = None
    research_gaps: List[ResearchGap] = Field(default_factory=list)
    report: Optional["ResearchReport"] = None
    errors: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ── Final report ────────────────────────────────────────────────────────────

class ResearchReport(BaseModel):
    question: str
    executive_summary: str
    literature_overview: str
    search_strategy: List[str] = Field(default_factory=list)
    key_findings: List[str] = Field(default_factory=list)
    methodology_comparison: Optional[str] = None
    contradictions: List[str] = Field(default_factory=list)
    research_gaps: List[ResearchGap] = Field(default_factory=list)
    validated_claims: List[ValidatedClaim] = Field(default_factory=list)
    papers_analyzed: List[PaperMetadata] = Field(default_factory=list)
    limitations: Optional[str] = None
    references: List[str] = Field(default_factory=list)
