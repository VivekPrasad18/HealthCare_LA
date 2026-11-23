"""
Evidence Extraction Agent.

For each retrieved paper, extracts structured research information using the LLM
(objective, dataset, methodology, results, limitations, etc.).
Missing fields are recorded as "Not reported" rather than fabricated.
"""

from __future__ import annotations
import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.schemas.evidence import ExtractedEvidence
from app.schemas.research import AgentState
from app.utils.llm import get_llm, extract_text
from app.utils.logging import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a systematic evidence extractor for scientific papers.
Given a paper title and abstract, extract the following fields.
If a field is not mentioned, write "Not reported".
Respond ONLY with valid JSON — no extra text.

{
  "research_objective": "...",
  "dataset": "...",
  "sample_size": "...",
  "methodology": "...",
  "evaluation_metrics": ["...", "..."],
  "main_results": "...",
  "key_findings": "...",
  "limitations": "..."
}"""


def _extract_one(paper_id: str, title: str, abstract: str | None) -> ExtractedEvidence:
    if not abstract:
        return ExtractedEvidence(
            paper_id=paper_id,
            title=title,
            research_objective="Not reported — no abstract available.",
        )

    llm = get_llm()
    prompt = f"Title: {title}\n\nAbstract:\n{abstract}"
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]
    response = llm.invoke(messages)
    raw = extract_text(response)

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning(f"Evidence agent: JSON parse failed for '{title[:40]}'")
        data = {}

    return ExtractedEvidence(
        paper_id=paper_id,
        title=title,
        research_objective=data.get("research_objective", "Not reported"),
        dataset=data.get("dataset", "Not reported"),
        sample_size=data.get("sample_size", "Not reported"),
        methodology=data.get("methodology", "Not reported"),
        evaluation_metrics=data.get("evaluation_metrics", []),
        main_results=data.get("main_results", "Not reported"),
        key_findings=data.get("key_findings", "Not reported"),
        limitations=data.get("limitations", "Not reported"),
    )


def run_evidence_agent(state: AgentState) -> AgentState:
    """LangGraph node: extract structured evidence from each retrieved paper."""
    logger.info(f"Evidence Agent: processing {len(state.retrieved_papers)} papers.")
    results = []

    for paper in state.retrieved_papers:
        paper_id = paper.doi or paper.pmid or paper.title[:20]
        try:
            ev = _extract_one(paper_id, paper.title, paper.abstract)
            results.append(ev)
        except Exception as exc:
            logger.warning(f"Evidence extraction failed for '{paper.title[:40]}': {exc}")

    state.extracted_evidence = results
    logger.info(f"Evidence Agent: extracted evidence from {len(results)} papers.")
    return state
