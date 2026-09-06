"""
SQLite connection/session management.
Reminder (SAS section 10): embeddings never go here — see chroma_client.py.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import get_settings
from models.base import Base

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create all tables. Called once on FastAPI startup (see main.py)."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency that yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
