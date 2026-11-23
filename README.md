# Healthcare Literature Analysis — Agentic AI + RAG Framework

An intelligent research assistant that automatically searches, retrieves, analyzes, and synthesizes healthcare and biomedical scientific literature using **Agentic AI**, **RAG**, and **LLMs**.

---

## What it does

Given a healthcare research question (e.g. *"What are recent ML approaches for early detection of diabetic retinopathy?"*), the system:

1. Decomposes the question into sub-questions and search queries (Research Agent)
2. Retrieves relevant papers from **PubMed** and **Semantic Scholar** (Literature Retrieval)
3. Chunks and embeds paper abstracts/text into **Qdrant** vector store (RAG Pipeline)
4. Extracts structured evidence per paper — objective, dataset, methodology, results (Evidence Agent)
5. Validates key claims against retrieved source passages (Validation Agent)
6. Synthesizes findings across all papers, identifying contradictions (Synthesis Agent)
7. Identifies research gaps grounded in the literature (Gap Analysis Agent)
8. Produces a **structured report** with citations and evidence grading (Report Agent)

---

## Project Structure

```
app/
├── main.py                  # FastAPI entry point
├── agents/
│   ├── research_agent.py    # Question decomposition + literature retrieval
│   ├── evidence_agent.py    # Structured extraction per paper
│   ├── validation_agent.py  # Claim ↔ source passage verification
│   ├── synthesis_agent.py   # Cross-paper comparison + contradiction detection
│   ├── gap_agent.py         # Research gap identification
│   ├── report_agent.py      # Final report generation
│   └── workflow.py          # LangGraph DAG connecting all agents
├── rag/
│   ├── chunking.py          # Fixed-size sentence-aware text chunking
│   ├── embeddings.py        # sentence-transformers / OpenAI embeddings
│   ├── vector_store.py      # Qdrant upsert + search
│   ├── retriever.py         # Query embedding + top-k retrieval
│   └── pipeline.py          # End-to-end ingest (process → embed → store)
├── literature/
│   ├── pubmed.py            # PubMed Entrez API
│   ├── semantic_scholar.py  # Semantic Scholar API
│   └── metadata.py          # Normalisation + deduplication
├── documents/
│   ├── pdf_loader.py        # PyMuPDF page extraction
│   ├── parser.py            # Section detection + text cleaning
│   └── processor.py         # PDF/abstract → PaperChunk objects
├── database/
│   ├── database.py          # SQLAlchemy engine + session
│   ├── models.py            # ORM models (Paper, Chunk, Evidence, Session)
│   └── crud.py              # CRUD helpers
├── schemas/
│   ├── paper.py             # PaperMetadata, PaperChunk
│   ├── evidence.py          # ExtractedEvidence, ValidatedClaim, ResearchGap
│   └── research.py          # AgentState, ResearchReport, API schemas
└── utils/
    ├── config.py            # Centralised settings from .env
    ├── logging.py           # Structured logger
    └── llm.py               # LLM provider wrapper (Google/OpenAI/Anthropic)
```

---

## Quick Start

### 1. Prerequisites

- Python 3.11+
- Docker + Docker Compose (for Qdrant + PostgreSQL)

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Copy `.env` and fill in your API keys:

```bash
# Required — choose one LLM provider:
GOOGLE_API_KEY=your_key      # for Gemini (default)
OPENAI_API_KEY=your_key      # for GPT-4
ANTHROPIC_API_KEY=your_key   # for Claude

LLM_PROVIDER=google
LLM_MODEL=gemini-1.5-flash
PUBMED_EMAIL=your@email.com
```

### 4. Start Qdrant + PostgreSQL

```bash
docker-compose up qdrant postgres -d
```

### 5. Run the API

```bash
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`

### 6. Run the full stack with Docker

```bash
docker-compose up --build
```

---

## API Usage

### Submit a research question

```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"question": "What are recent machine learning approaches for early detection of diabetic retinopathy?", "max_papers": 10}'
```

### Response structure

```json
{
  "question": "...",
  "session_id": "uuid",
  "report": {
    "executive_summary": "...",
    "key_findings": ["...", "..."],
    "research_gaps": [{"gap_description": "...", "gap_type": "dataset"}],
    "validated_claims": [{"claim": "...", "validation_status": "supported"}],
    "references": ["[1] Author et al. (2023). Title. DOI: ..."],
    ...
  }
}
```

---

## LLM Provider Configuration

| Provider | `LLM_PROVIDER` | `LLM_MODEL` |
|---|---|---|
| Google Gemini | `google` | `gemini-1.5-flash` or `gemini-1.5-pro` |
| OpenAI | `openai` | `gpt-4o` or `gpt-4-turbo` |
| Anthropic | `anthropic` | `claude-3-5-sonnet-20241022` |

---

## Important Notes

- This system is for **academic and research use only**.
- It is **not** a clinical diagnosis system and does not provide patient-specific recommendations.
- Generated reports should be verified against original sources before citation.
- Results quality depends on the LLM provider and the number of papers retrieved.
