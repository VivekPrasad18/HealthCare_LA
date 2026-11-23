"""
FastAPI application entry point.

Endpoints:
  POST /research          — run the full multi-agent research workflow
  GET  /research/{id}     — retrieve a past report by session ID
  GET  /health            — liveness check
"""

from __future__ import annotations
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.agents.workflow import run_research_workflow
from app.database.database import get_db, create_tables
from app.database.crud import create_session, save_report, get_session
from app.schemas.research import ResearchRequest, ResearchResponse, ResearchReport
from app.utils.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Healthcare Literature Analysis API",
    description="Agentic AI + RAG framework for evidence-grounded healthcare literature analysis.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the frontend
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/", include_in_schema=False)
def serve_ui():
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"message": "Frontend not found. Place index.html in /frontend/"}


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up — creating database tables.")
    try:
        create_tables()
    except Exception as exc:
        logger.warning(f"Database init failed (is PostgreSQL running?): {exc}")


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


@app.post("/research", response_model=ResearchResponse)
def run_research(
    request: ResearchRequest,
    db: Session = Depends(get_db),
):
    """
    Submit a healthcare research question and receive a full literature analysis report.
    The workflow runs synchronously; expect 30–120 seconds depending on paper count.
    """
    session_id = str(uuid.uuid4())
    logger.info(f"[{session_id}] New research request: {request.question[:80]}")

    # Persist session
    try:
        create_session(db, request.question)
    except Exception:
        pass  # DB may not be available; don't block the research run

    try:
        report: ResearchReport = run_research_workflow(
            question=request.question,
            max_papers=request.max_papers,
        )
    except Exception as exc:
        logger.error(f"[{session_id}] Workflow error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

    # Save report
    try:
        save_report(db, session_id, report)
    except Exception:
        pass

    return ResearchResponse(
        question=request.question,
        report=report,
        session_id=session_id,
    )


@app.get("/research/{session_id}", response_model=ResearchResponse)
def get_research(session_id: str, db: Session = Depends(get_db)):
    """Retrieve a previously generated report by session ID."""
    session = get_session(db, session_id)
    if not session or not session.report_json:
        raise HTTPException(status_code=404, detail="Session not found.")

    report = ResearchReport.model_validate_json(session.report_json)
    return ResearchResponse(
        question=session.question,
        report=report,
        session_id=session_id,
    )
