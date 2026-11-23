"""
Research Agent — entry point of the multi-agent workflow.

Responsibilities:
  1. Parse the research question.
  2. Decompose it into focused sub-questions.
  3. Generate targeted literature search queries for each sub-question.
  4. Trigger literature retrieval and RAG ingestion.
  5. Populate AgentState with retrieved papers.
"""

from __future__ import annotations
import json
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage

from app.literature.pubmed import query_pubmed
from app.literature.semantic_scholar import query_semantic_scholar
from app.literature.metadata import merge_sources
from app.rag.pipeline import ingest_paper
from app.schemas.research import AgentState
from app.utils.llm import get_llm, extract_text
from app.utils.logging import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a biomedical research assistant.
Your task is to analyse a healthcare research question and produce:
1. A list of 3–5 focused sub-questions that together cover the original question.
2. 2–3 specific literature search queries per sub-question (suitable for PubMed/Semantic Scholar).

Respond ONLY with valid JSON in this exact format:
{
  "sub_questions": ["...", "..."],
  "search_queries": ["...", "...", "..."]
}
Do not include any text outside the JSON block."""


def _llm_decompose(question: str) -> tuple[List[str], List[str]]:
    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Research question: {question}"),
    ]
    response = llm.invoke(messages)
    raw = extract_text(response)

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        data = json.loads(raw)
        return data.get("sub_questions", []), data.get("search_queries", [])
    except json.JSONDecodeError:
        logger.warning("Research agent: failed to parse LLM JSON, using fallback.")
        return [question], [question]


def run_research_agent(state: AgentState, max_papers_per_query: int = 5) -> AgentState:
    """
    LangGraph node function.
    Mutates and returns *state* with sub_questions, search_queries, and retrieved_papers.
    """
    logger.info(f"Research Agent: processing question: {state.question[:80]}")

    sub_questions, search_queries = _llm_decompose(state.question)
    state.sub_questions = sub_questions
    state.search_queries = search_queries
    logger.info(f"Generated {len(sub_questions)} sub-questions, {len(search_queries)} queries.")

    # Retrieve from both sources
    all_pubmed: list = []
    all_ss: list = []

    for query in search_queries:
        logger.info(f"Searching: {query}")
        try:
            pm = query_pubmed(query, max_results=max_papers_per_query)
            all_pubmed.extend(pm)
        except Exception as exc:
            logger.warning(f"PubMed query failed: {exc}")
        try:
            ss = query_semantic_scholar(query, max_results=max_papers_per_query)
            all_ss.extend(ss)
        except Exception as exc:
            logger.warning(f"Semantic Scholar query failed: {exc}")

    papers = merge_sources(all_pubmed, all_ss)
    state.retrieved_papers = papers
    logger.info(f"Research Agent: retrieved {len(papers)} unique papers.")

    # Ingest abstracts into Qdrant (no PDF at this stage)
    for meta in papers:
        try:
            ingest_paper(meta, pdf_source=None)
        except Exception as exc:
            logger.warning(f"Ingest failed for '{meta.title[:40]}': {exc}")

    return state
