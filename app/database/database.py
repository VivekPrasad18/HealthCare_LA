"""
SQLAlchemy engine and session factory.
The engine is created lazily on first use so the app starts even when
PostgreSQL is not yet available (useful for development without Docker).
"""

from __future__ import annotations
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.utils.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

Base = declarative_base()

_engine = None
_SessionLocal = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            echo=settings.DEBUG,
        )
        logger.info(f"Database engine created: {settings.DATABASE_URL.split('@')[-1]}")
    return _engine


def _get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_get_engine())
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency — yields a DB session and closes it on exit."""
    factory = _get_session_factory()
    db = factory()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables. Called once at startup."""
    from app.database import models  # noqa: F401 — registers models with Base
    try:
        Base.metadata.create_all(bind=_get_engine())
        logger.info("Database tables created / verified.")
    except Exception as exc:
        logger.warning(f"Could not create tables (is PostgreSQL running?): {exc}")


def check_db_connection() -> bool:
    """Returns True if the database is reachable."""
    try:
        with _get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
