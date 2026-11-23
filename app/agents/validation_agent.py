"""
Evidence Validation Agent.

For each key claim in the extracted evidence, retrieves the most relevant
RAG chunks and checks whether the claim is supported by the source passage.

Validation statuses:
  supported | partially_supported | unsupported | insufficient_evidence
"""

from __future__ import annotations
import json
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage

from app.rag.retriever import retrieve
from app.schemas.evidence import ValidatedClaim, ValidationStatus
from app.schemas.research import AgentState
from app.utils.llm import get_llm, extract_text
from app.utils.logging import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a scientific claim validator.
Given a claim and a source passage from a scientific paper, determine whether the passage supports the claim.

Respond ONLY with valid JSON:
{
  "status": "supported" | "partially_supported" | "unsupported" | "insufficient_evidence",
  "confidence": <float 0.0–1.0>,
  "explanation": "one sentence"
}"""


def _validate_claim(claim: str, source_passage: str, source_paper_id: str, chunk_id: str | None) -> ValidatedClaim:
    llm = get_llm()
    prompt = f"Claim: {claim}\n\nSource passage:\n{source_passage}"
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
        status = ValidationStatus(data.get("status", "insufficient_evidence"))
        confidence = float(data.get("confidence", 0.0))
    except (json.JSONDecodeError, ValueError):
        status = ValidationStatus.INSUFFICIENT_EVIDENCE
        confidence = 0.0

    return ValidatedClaim(
        claim=claim,
        source_paper_id=source_paper_id,
        source_chunk_id=chunk_id,
        source_passage=source_passage[:500],
        validation_status=status,
        confidence=confidence,
    )


def _claims_from_evidence(evidence) -> List[str]:
    """Pull the most important verifiable claims from an evidence record."""
    claims = []
    if evidence.key_findings and evidence.key_findings != "Not reported":
        claims.append(evidence.key_findings[:300])
    if evidence.main_results and evidence.main_results != "Not reported":
        claims.append(evidence.main_results[:300])
    return claims


def run_validation_agent(state: AgentState) -> AgentState:
    """LangGraph node: validate key claims against retrieved RAG chunks."""
    logger.info(f"Validation Agent: validating claims from {len(state.extracted_evidence)} papers.")
    validated: List[ValidatedClaim] = []

    for ev in state.extracted_evidence:
        claims = _claims_from_evidence(ev)
        for claim in claims:
            # Retrieve supporting passages for this specific claim
            chunks = retrieve(claim, top_k=3)
            if not chunks:
                validated.append(
                    ValidatedClaim(
                        claim=claim,
                        source_paper_id=ev.paper_id,
                        validation_status=ValidationStatus.INSUFFICIENT_EVIDENCE,
                    )
                )
                continue

            # Use the top-scoring chunk as the source passage
            top_chunk = chunks[0]
            try:
                result = _validate_claim(
                    claim=claim,
                    source_passage=top_chunk.get("text", ""),
                    source_paper_id=top_chunk.get("paper_id", ev.paper_id),
                    chunk_id=top_chunk.get("chunk_id"),
                )
                validated.append(result)
            except Exception as exc:
                logger.warning(f"Validation failed for claim: {claim[:60]}: {exc}")

    state.validated_claims = validated
    logger.info(f"Validation Agent: produced {len(validated)} validated claims.")
    return state
