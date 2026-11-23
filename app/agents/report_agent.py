"""
Report Generation Agent.

Combines all agent outputs into a structured ResearchReport with citations.
"""

from __future__ import annotations
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage

from app.schemas.research import AgentState, ResearchReport
from app.utils.llm import get_llm, extract_text
from app.utils.logging import get_logger

logger = get_logger(__name__)

SUMMARY_PROMPT = """You are a scientific report writer.
Write a concise executive summary (150–200 words) for a healthcare literature analysis report.
Base it strictly on the provided synthesis and question.
Do not add information not present in the synthesis."""

FINDINGS_PROMPT = """Extract 5–8 key findings as a bullet-point list from the synthesis below.
Each finding should be a single clear sentence grounded in the retrieved literature.
Respond with one finding per line, no numbering, no bullet symbols — just plain lines."""


def _generate_summary(question: str, synthesis: str) -> str:
    llm = get_llm()
    messages = [
        SystemMessage(content=SUMMARY_PROMPT),
        HumanMessage(content=f"Question: {question}\n\nSynthesis:\n{synthesis}"),
    ]
    return extract_text(llm.invoke(messages))


def _extract_findings(synthesis: str) -> List[str]:
    llm = get_llm()
    messages = [
        SystemMessage(content=FINDINGS_PROMPT),
        HumanMessage(content=synthesis),
    ]
    raw = extract_text(llm.invoke(messages))
    return [line.strip() for line in raw.splitlines() if line.strip()]


def _extract_contradictions(synthesis: str) -> List[str]:
    """Pull contradiction sentences from the synthesis (heuristic)."""
    contradictions = []
    for line in synthesis.splitlines():
        line_l = line.lower()
        if any(kw in line_l for kw in ["contradict", "conflict", "disagree", "inconsistent", "however", "whereas"]):
            contradictions.append(line.strip())
    return contradictions[:5]


def _format_references(papers) -> List[str]:
    refs = []
    for i, p in enumerate(papers, start=1):
        authors = ", ".join(p.authors[:3]) + (" et al." if len(p.authors) > 3 else "")
        year = p.year or "n.d."
        doi = f" DOI: {p.doi}" if p.doi else ""
        url = f" {p.url}" if p.url else ""
        refs.append(f"[{i}] {authors} ({year}). {p.title}.{doi}{url}")
    return refs


def run_report_agent(state: AgentState) -> AgentState:
    """LangGraph node: produce the final ResearchReport."""
    logger.info("Report Agent: generating final report.")

    synthesis = state.synthesis or "Synthesis not available."
    summary = _generate_summary(state.question, synthesis)
    findings = _extract_findings(synthesis)
    contradictions = _extract_contradictions(synthesis)
    references = _format_references(state.retrieved_papers)

    literature_overview = (
        f"This analysis reviewed {len(state.retrieved_papers)} papers retrieved from "
        f"PubMed and Semantic Scholar in response to the question: \"{state.question}\". "
        f"Papers were processed using abstract-level RAG and evidence extraction."
    )

    report = ResearchReport(
        question=state.question,
        executive_summary=summary,
        literature_overview=literature_overview,
        search_strategy=state.search_queries,
        key_findings=findings,
        methodology_comparison=synthesis,
        contradictions=contradictions,
        research_gaps=state.research_gaps,
        validated_claims=state.validated_claims,
        papers_analyzed=state.retrieved_papers,
        limitations=(
            "This analysis is based on abstracts only. Full-text analysis may yield additional findings. "
            "LLM-generated summaries may not capture all nuances of the original papers."
        ),
        references=references,
    )

    state.report = report
    logger.info("Report Agent: report complete.")
    return state
