"""
Central configuration for AgentOS backend.

All environment-driven values must be read through this module.
No direct os.environ calls should be used elsewhere in the codebase.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ============================================================
    # Application
    # ============================================================

    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # ============================================================
    # CORS
    # ============================================================

    CORS_ORIGINS: List[str] = [
        "http://localhost:5173"
    ]

    # ============================================================
    # LLM Provider
    # ============================================================

    LLM_PROVIDER: str = "groq"

    # ============================================================
    # Groq
    # ============================================================

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    GROQ_TIMEOUT: float = 10.0
    GROQ_MAX_RETRIES: int = 0

    # ============================================================
    # Gemini
    # ============================================================

    GEMINI_API_KEY: str = ""

    # ============================================================
    # Embeddings
    # ============================================================

    EMBEDDING_MODEL: str = "gemini-embedding-2"
    EMBEDDING_DIMENSIONALITY: int = 768

    # ============================================================
    # Database
    # ============================================================

    DATABASE_URL: str = "sqlite:///./database/agentos.db"

    # ============================================================
    # ChromaDB
    # ============================================================

    CHROMA_PERSIST_DIR: str = "./database/chroma_store"
    CHROMA_COLLECTION_NAME: str = "document_embeddings"

    # ============================================================
    # Document Processing
    # ============================================================

    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 120

    SUPPORTED_DOCUMENT_TYPES: List[str] = [
        ".pdf",
        ".docx",
        ".txt",
    ]

    # ============================================================
    # Retrieval
    # ============================================================

    SEMANTIC_TOP_K: int = 5
    BM25_TOP_K: int = 5
    FINAL_TOP_K: int = 3

    SEMANTIC_WEIGHT: float = 0.65
    BM25_WEIGHT: float = 0.35

    # Relevance calibration
    SEMANTIC_DISTANCE_THRESHOLD: float = 0.85
    BM25_MIN_SCORE: float = 1.20

    # ============================================================
    # Storage
    # ============================================================

    UPLOAD_DIR: str = "./uploads"
    REPORTS_DIR: str = "./reports"

    SESSION_EXPIRY_HOURS: int = 24

    # ============================================================
    # Environment Configuration
    # ============================================================

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """
    Return the cached application settings.
    """

    return Settings()