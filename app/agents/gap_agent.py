"""
Research Gap Analysis Agent.

Analyses the synthesized literature to identify potential research gaps:
  - Dataset limitations (small size, single-site, lack of diversity)
  - Methodological gaps (missing baselines, lack of explainability)
  - Understudied populations
  - Unresolved contradictions
  - Future directions explicitly mentioned by authors

All identified gaps are grounded in the analyzed papers.
"""

from __future__ import annotations
import json
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage

from app.schemas.evidence import ResearchGap
from app.schemas.research import AgentState
from app.utils.llm import get_llm, extract_text
from app.utils.logging import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a research gap analyst for biomedical literature.
Based on the synthesis and evidence below, identify 3–7 specific research gaps.

For each gap, provide:
- A clear description (1–2 sentences)
- The gap type: dataset | methodology | population | reproducibility | explainability | general
- Which paper(s) support this gap (use paper titles)

Respond ONLY with valid JSON:
{
  "gaps": [
    {
      "gap_description": "...",
      "gap_type": "...",
      "supporting_paper_titles": ["...", "..."]
    }
  ]
}"""


def run_gap_agent(state: AgentState) -> AgentState:
    """LangGraph node: identify research gaps from the synthesized literature."""
    if not state.synthesis and not state.extracted_evidence:
        logger.warning("Gap Agent: no synthesis or evidence to analyze.")
        state.research_gaps = []
        return state

    logger.info("Gap Agent: analyzing research gaps.")

    # Build input for the LLM
    paper_titles = {
        (ev.paper_id): ev.title
        for ev in state.extracted_evidence
    }
    limitations_summary = "\n".join(
        f"- {ev.title}: {ev.limitations}"
        for ev in state.extracted_evidence
        if ev.limitations and ev.limitations != "Not reported"
    )

    input_text = (
        f"Research question: {state.question}\n\n"
        f"Synthesis:\n{state.synthesis or 'Not available'}\n\n"
        f"Reported limitations per paper:\n{limitations_summary or 'None available'}"
    )

    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=input_text),
    ]
    response = llm.invoke(messages)
    raw = extract_text(response)

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    gaps: List[ResearchGap] = []
    try:
        data = json.loads(raw)
        for g in data.get("gaps", []):
            # Map supporting titles back to paper IDs (best-effort)
            supporting_ids = []
            for title in g.get("supporting_paper_titles", []):
                for pid, ptitle in paper_titles.items():
                    if title.lower() in ptitle.lower() or ptitle.lower() in title.lower():
                        supporting_ids.append(pid)
                        break

            gaps.append(
                ResearchGap(
                    gap_description=g.get("gap_description", ""),
                    gap_type=g.get("gap_type", "general"),
                    supporting_paper_ids=supporting_ids,
                )
            )
    except json.JSONDecodeError:
        logger.warning("Gap Agent: JSON parse failed, extracting raw text as single gap.")
        gaps.append(ResearchGap(gap_description=raw[:500], gap_type="general"))

    state.research_gaps = gaps
    logger.info(f"Gap Agent: identified {len(gaps)} research gap(s).")
    return state
