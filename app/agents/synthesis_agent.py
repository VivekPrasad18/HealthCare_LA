"""
Literature Synthesis Agent.

Compares findings across all extracted evidence records:
  - Common methodologies and datasets
  - Consistent findings across studies
  - Contradictory or conflicting results
  - Methodology comparison table (as text)

Produces a synthesis narrative stored in state.synthesis.
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.schemas.research import AgentState
from app.utils.llm import get_llm, extract_text
from app.utils.logging import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a systematic literature synthesis expert.
You will receive structured evidence extracted from multiple scientific papers.
Write a concise synthesis (400–600 words) that:
1. Compares methodologies and datasets used across studies.
2. Identifies consistent findings that appear in multiple papers.
3. Identifies contradictory or conflicting results (be specific — cite paper titles).
4. Notes common limitations across studies.
5. Remains strictly grounded in the provided evidence — do not add external knowledge.

Write in clear academic English. Use paper titles (not author names, since they may not be available) when making specific comparisons."""


def _format_evidence_for_llm(state: AgentState) -> str:
    lines = [f"Research question: {state.question}\n"]
    for i, ev in enumerate(state.extracted_evidence, start=1):
        lines.append(
            f"Paper {i}: {ev.title}\n"
            f"  Objective: {ev.research_objective}\n"
            f"  Dataset: {ev.dataset}\n"
            f"  Methodology: {ev.methodology}\n"
            f"  Metrics: {', '.join(ev.evaluation_metrics) if ev.evaluation_metrics else 'Not reported'}\n"
            f"  Results: {ev.main_results}\n"
            f"  Findings: {ev.key_findings}\n"
            f"  Limitations: {ev.limitations}\n"
        )
    return "\n".join(lines)


def run_synthesis_agent(state: AgentState) -> AgentState:
    """LangGraph node: synthesize findings across all retrieved papers."""
    if not state.extracted_evidence:
        state.synthesis = "No evidence available for synthesis."
        logger.warning("Synthesis Agent: no extracted evidence to synthesize.")
        return state

    logger.info(f"Synthesis Agent: synthesizing {len(state.extracted_evidence)} papers.")
    evidence_text = _format_evidence_for_llm(state)
    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=evidence_text),
    ]
    response = llm.invoke(messages)
    state.synthesis = extract_text(response)
    logger.info("Synthesis Agent: synthesis complete.")
    return state
