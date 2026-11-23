# An Agentic AI and RAG-Based Framework for Evidence-Grounded Healthcare Literature Analysis

---

## Abstract

The exponential growth of biomedical publications has made manual literature review increasingly impractical for researchers and students. General-purpose Large Language Models (LLMs) can summarize and answer questions but are prone to hallucination when not grounded in verified sources. Basic Retrieval-Augmented Generation (RAG) systems improve factual grounding but fall short on complex research tasks requiring multi-step reasoning, structured evidence extraction, and cross-paper synthesis. This paper proposes an agentic AI framework that integrates biomedical literature retrieval, RAG, claim-level evidence validation, multi-document synthesis, and research gap identification to support evidence-grounded healthcare literature analysis. The framework orchestrates specialized agents using LangGraph, retrieves scientific literature from PubMed and Semantic Scholar, stores document embeddings in Qdrant, and produces structured research reports with traceable citations. The system is designed for academic and research use and is not intended for clinical diagnosis or patient-specific recommendations.

**Index Terms** — Agentic AI, Retrieval-Augmented Generation, Healthcare Literature Analysis, Large Language Models, Biomedical Information Retrieval, Evidence Extraction, Evidence Validation, Multi-Agent Systems, Model Context Protocol

---

## I. Introduction

Biomedical and healthcare research generates thousands of new publications each year. Researchers must manually search multiple databases, read and synthesize papers, compare methodologies, extract findings, and identify gaps — a process that is both time-intensive and cognitively demanding.

Conventional keyword-based literature search engines such as PubMed retrieve relevant documents but do not analyze, compare, or synthesize them. General-purpose LLMs can generate plausible summaries and answer questions in natural language, but without grounding in retrieved sources, they may produce hallucinated references or unsupported conclusions — a critical concern in healthcare contexts.

Basic RAG systems reduce hallucination by conditioning generation on retrieved document chunks. However, single-query RAG pipelines are insufficient for complex research questions that require decomposition into multiple sub-questions, iterative retrieval, structured extraction of experimental details, claim verification, cross-paper comparison, and research gap discovery.

Agentic AI systems address these limitations by decomposing tasks, coordinating specialized tools and sub-agents, and reasoning iteratively over retrieved knowledge. Applied to biomedical literature, an agentic framework can automate the full pipeline from question understanding to traceable report generation.

This paper proposes such a framework — a multi-agent, evidence-grounded system for healthcare literature analysis. The main contributions are:

1. A modular agentic architecture that decomposes healthcare research questions and coordinates specialized agents for retrieval, extraction, validation, synthesis, and gap analysis.
2. An evidence-grounded RAG pipeline that maps generated claims to source passages with explicit validation status (Supported / Partially Supported / Unsupported / Insufficient Evidence).
3. Integration of MCP (Model Context Protocol) for standardized, interoperable access to literature, document, and database tools.
4. A structured report generation pipeline that produces citation-traceable research analyses.

The remainder of this paper is organized as follows. Section II reviews related work. Section III describes the proposed methodology and architecture. Section IV covers the implementation. Section V presents results and discussion. Section VI concludes with limitations and future directions.

---

## II. Related Work

### A. Biomedical Information Retrieval

PubMed remains the primary repository for indexed biomedical literature, providing structured access via the NCBI Entrez API. Semantic Scholar extends retrieval with citation graph analysis and open-access full-text links. Prior work on biomedical retrieval has focused on improving query expansion, MeSH term mapping, and relevance ranking [CITE]. However, these systems return document lists and do not perform downstream analysis.

### B. Large Language Models in Healthcare

LLMs such as GPT-4, Gemini, and Claude have shown strong performance on medical question-answering benchmarks. However, studies have documented hallucination risks in clinical and biomedical contexts [CITE]. Models trained on web-scale corpora may confidently generate plausible but incorrect clinical or scientific claims. This underscores the need for retrieval-augmented and evidence-validated generation pipelines.

### C. Retrieval-Augmented Generation

RAG [Lewis et al., 2020] conditions LLM generation on retrieved document passages, substantially reducing hallucination on knowledge-intensive tasks. Biomedical adaptations of RAG have been proposed for clinical report analysis and evidence-based question answering [CITE]. These systems improve factual accuracy but are typically single-stage pipelines lacking structured evidence extraction or claim verification.

### D. Evidence-Grounded Question Answering

Evidence grounding extends RAG by explicitly linking generated statements to supporting passages and assessing whether retrieved evidence supports, partially supports, or contradicts each claim. Work in this area includes [CITE] and is closely related to fact-checking and citation attribution research. Healthcare-specific evidence grounding remains an open challenge.

### E. Hallucination Detection and Mitigation

Methods for detecting LLM hallucinations range from consistency checking across multiple outputs to passage-level entailment verification using NLI models [CITE]. Recent approaches integrate hallucination detection into the generation pipeline rather than applying it as a post-hoc filter. The proposed framework adopts a similar inline validation approach through its Evidence Validation Agent.

### F. Agentic AI and Multi-Agent Systems

Agentic LLM frameworks such as ReAct [Yao et al., 2022], AutoGPT, and LangGraph enable LLMs to reason step-by-step, use external tools, and coordinate with other agents. Multi-agent systems have been applied to software engineering, research summarization, and data analysis [CITE]. Their application to structured biomedical literature analysis is relatively unexplored.

### G. Model Context Protocol (MCP)

MCP is a recently proposed standard for providing LLM agents with structured access to external tools and data sources through a consistent interface. Its application to biomedical literature retrieval and database integration offers a pathway to modular, interoperable agentic systems [CITE].

### H. Research Automation

Automated systematic review tools such as Rayyan and Covidence assist with paper screening and data extraction but rely heavily on human judgment. Fully automated literature synthesis using LLMs has been explored in [CITE] but lacks structured evidence validation and research gap analysis. The proposed framework addresses these gaps.

**Research Gap Identified:** No existing system combines multi-agent orchestration, biomedical multi-source retrieval, claim-level evidence validation with explicit grounding status, structured cross-paper synthesis, and MCP-based tool integration into a single end-to-end framework for healthcare literature analysis.

---

## III. Proposed Methodology

### A. System Architecture Overview

The proposed framework consists of seven layers:

1. **User Interface Layer** — Web frontend (React/Next.js) or prototype UI (Streamlit) for query input and report display.
2. **Backend Layer** — FastAPI server handling request routing, session management, and agent coordination.
3. **Agent Orchestration Layer** — LangGraph workflow managing agent state, task routing, and conditional branching.
4. **Literature Retrieval Layer** — PubMed and Semantic Scholar API integrations for paper search, metadata retrieval, and abstract/full-text collection.
5. **RAG Layer** — Document chunking, embedding generation (BGE / Sentence Transformers), and semantic retrieval from Qdrant vector store.
6. **Evidence Analysis Layer** — Structured extraction, claim validation, cross-paper synthesis, and gap analysis.
7. **Report Generation Layer** — Structured output with citations, evidence passages, and research gap summaries.

```
User Query
    │
    ▼
Research Agent (Question Decomposition + Query Generation)
    │
    ▼
Literature Retrieval Agent (PubMed + Semantic Scholar)
    │
    ▼
Document Processing (PDF Extraction → Cleaning → Chunking → Embedding → Qdrant)
    │
    ▼
RAG Retrieval (Semantic Search → Context Construction)
    │
    ▼
Evidence Extraction Agent (Structured Information Extraction)
    │
    ▼
Evidence Validation Agent (Claim ↔ Source Passage Verification)
    │
    ▼
Synthesis Agent (Cross-Paper Comparison + Contradiction Detection)
    │
    ▼
Gap Analysis Agent (Research Gap Identification)
    │
    ▼
Report Generation Agent (Structured Report + Citations)
    │
    ▼
User Receives Traceable Research Analysis
```

### B. Research Agent

The Research Agent is the central orchestrator. Given a healthcare research question, it:

- Parses the research objective.
- Decomposes the question into searchable sub-topics.
- Generates multiple targeted search queries for each sub-topic.
- Determines whether additional retrieval iterations are necessary based on coverage.
- Coordinates handoff between downstream agents.

### C. Literature Retrieval

The system queries PubMed using the NCBI Entrez Utilities API (E-utilities) and Semantic Scholar using its Open Research Corpus API. For each query, the system retrieves:

- Paper title, authors, publication year, DOI, PMID.
- Abstract text.
- Full-text content where available and legally accessible.

The system deduplicates results by DOI/PMID and filters papers by relevance score. It explicitly records whether each paper was analyzed using full text or abstract only.

### D. Document Processing Pipeline

Retrieved documents pass through:

1. **PDF text extraction** using PyMuPDF.
2. **Text cleaning** — removal of headers, footers, and formatting artifacts.
3. **Section identification** — abstract, introduction, methods, results, discussion.
4. **Chunking** — fixed-size with overlap to preserve context across chunk boundaries.
5. **Metadata tagging** — paper ID, title, authors, year, DOI, section, chunk ID.
6. **Embedding generation** — dense vectors using BGE or Sentence Transformers.
7. **Vector storage** — indexed in Qdrant with metadata for filtered retrieval.

### E. RAG Pipeline

User research questions are embedded and used to query Qdrant for the top-k most semantically similar chunks. Retrieved chunks form the context for LLM generation. The system constructs prompts that instruct the LLM to generate answers grounded in the provided context and to cite source chunk IDs for each factual claim.

### F. Evidence Extraction

The Evidence Extraction Agent processes each retrieved paper to populate a structured evidence record:

| Field | Description |
|---|---|
| Research Objective | What the paper aims to study |
| Study Population / Dataset | Patient cohort or dataset used |
| Sample Size | Number of subjects/samples |
| Methodology | Algorithms, models, study design |
| Evaluation Metrics | Accuracy, AUC, sensitivity, etc. |
| Main Results | Key quantitative findings |
| Key Findings | Author conclusions |
| Limitations | Reported constraints |

Fields not reported in the source paper are recorded as "Not Reported" rather than inferred.

### G. Evidence Validation

For each claim in the generated output, the Evidence Validation Agent:

1. Extracts individual claims using the LLM.
2. Retrieves the most relevant source chunk(s) for each claim from Qdrant.
3. Applies an NLI-based or LLM-based entailment check between the claim and the source passage.
4. Assigns a validation status:
   - **Supported** — source passage directly supports the claim.
   - **Partially Supported** — source passage is related but does not fully confirm the claim.
   - **Unsupported** — no retrieved passage supports the claim.
   - **Insufficient Evidence** — relevant passages exist but are inconclusive.

The final report includes validation status for each major claim.

### H. Literature Synthesis

The Synthesis Agent compares findings across all retrieved and analyzed papers:

- Methodology comparison (models, datasets, experimental setup).
- Result comparison (reported metrics, effect sizes).
- Identification of consistent findings across studies.
- Identification of contradictory or conflicting results.
- Preservation of individual study limitations.

### I. Research Gap Analysis

The Gap Analysis Agent reviews the synthesized literature to identify:

- Understudied populations or demographic groups.
- Dataset limitations (single-site, small sample, lack of diversity).
- Methodological gaps (missing baselines, lack of explainability, reproducibility issues).
- Unresolved contradictions in the literature.
- Future directions suggested by multiple studies.

All identified gaps must be traceable to specific papers in the retrieved set.

### J. MCP Integration

The system exposes literature retrieval, document access, and database operations through MCP servers:

- **Literature MCP Server**: `search_literature()`, `get_paper()`, `get_paper_metadata()`
- **Document MCP Server**: `list_documents()`, `read_document()`, `get_document_metadata()`
- **Database MCP Server**: `store_paper()`, `store_evidence()`, `retrieve_evidence()`

---

## IV. Implementation

### A. Development Environment

| Component | Technology |
|---|---|
| Programming Language | Python 3.11+ |
| Backend | FastAPI + Uvicorn |
| Agent Orchestration | LangGraph |
| LLM | Gemini / OpenAI / Claude (configurable) |
| Embeddings | BGE / Sentence Transformers |
| Vector Database | Qdrant |
| Relational Database | PostgreSQL |
| PDF Processing | PyMuPDF |
| Literature APIs | PubMed Entrez, Semantic Scholar |
| MCP | Python MCP SDK |
| Frontend | React / Next.js (prototype: Streamlit) |
| Containerization | Docker + Docker Compose |

### B. Literature Retrieval — PubMed Integration

The PubMed module uses the NCBI E-utilities API (esearch + efetch). Search queries are submitted to `esearch.fcgi` to obtain PMIDs, which are then passed to `efetch.fcgi` to retrieve structured XML records containing title, authors, abstract, publication year, and DOI. The module is implemented and operational.

> *[Note: Semantic Scholar, full-text processing, RAG, agent modules, and frontend are planned components. Only implemented components will be described as completed in the final paper.]*

---

## V. Results and Discussion

> *This section will be completed after experimental evaluation. The following evaluation plan defines the metrics and baselines.*

### A. Evaluation Plan

**Information Retrieval:**
- Precision@K, Recall@K, MRR, nDCG
- Evaluated against manually curated relevance judgments for a set of test research questions.

**Evidence Grounding:**
- Percentage of claims with Supported / Partially Supported / Unsupported / Insufficient Evidence status.
- Citation correctness rate.

**Hallucination Assessment:**
- Proportion of unsupported claims in outputs generated with vs. without the Evidence Validation Agent.

**Synthesis Quality:**
- Manual evaluation of cross-paper comparison correctness and contradiction detection accuracy.

**Baselines for Comparison:**
- LLM without RAG
- Single-query RAG without agents
- Agentic RAG without claim validation
- Proposed framework (full pipeline)

> All reported values in the final paper will be obtained through actual experiments. No performance figures are stated here without empirical data.

---

## VI. Conclusion and Future Work

This paper proposes an agentic AI framework for evidence-grounded healthcare literature analysis. The framework combines multi-agent orchestration, biomedical literature retrieval from PubMed and Semantic Scholar, RAG-based retrieval, structured evidence extraction, claim-level validation, multi-document synthesis, research gap analysis, and MCP-based tool integration.

The PubMed retrieval module is currently implemented. Remaining components — including the full agent pipeline, RAG layer, evidence validation, and frontend — are under active development.

**Future work includes:**
- Expanding retrieval to Crossref, arXiv, and institutional repositories.
- Incorporating citation graph analysis for deeper literature mapping.
- Developing a fine-tuned biomedical NLI model for more accurate claim validation.
- Adding user feedback mechanisms to refine retrieved results.
- Evaluating the system on domain-specific tasks (oncology, cardiology, ophthalmology).
- Formal user study with researchers and graduate students.

---

## References

> *The following are placeholder reference categories. All citations must be verified against actual IEEE Xplore, PubMed, or ACL Anthology records before submission. Do not use these as final citations.*

[1] Lewis, P., et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," NeurIPS 2020. *(Verify full citation)*

[2] Yao, S., et al., "ReAct: Synergizing Reasoning and Acting in Language Models," ICLR 2023. *(Verify full citation)*

[3] [IEEE paper on biomedical RAG hallucination reduction — verify via IEEE Xplore]

[4] [IEEE paper on evidence-based biomedical knowledge extraction — verify via IEEE Xplore]

[5] [IEEE paper on trustworthy LLMs in healthcare / Graph RAG — verify via IEEE Xplore]

[6] [IEEE paper on hallucination mitigation in medical QA — verify via IEEE Xplore]

[7] NCBI, "Entrez Programming Utilities Help," National Center for Biotechnology Information. [Online]. Available: https://www.ncbi.nlm.nih.gov/books/NBK25501/

[8] Qdrant, "Qdrant Vector Database Documentation." [Online]. Available: https://qdrant.tech/documentation/

---

*Draft prepared: November 2026. For internal use — do not submit before experimental results are added and all references are verified.*
