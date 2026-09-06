"""
Aggregates all v1 routers under one prefix.
"""

from fastapi import APIRouter

from api.v1.routes import (
    chat,
    upload,
    analyze,
    conversations,
    reports,
    health,
    documents,
)


api_router = APIRouter()


# ================================================================
# Health
# ================================================================

api_router.include_router(
    health.router,
    tags=["health"],
)


# ================================================================
# Chat
# ================================================================

api_router.include_router(
    chat.router,
    tags=["chat"],
)


# ================================================================
# Upload
# ================================================================

api_router.include_router(
    upload.router,
    tags=["upload"],
)


# ================================================================
# Analyze
# ================================================================

api_router.include_router(
    analyze.router,
    tags=["analyze"],
)


# ================================================================
# Conversations
# ================================================================

api_router.include_router(
    conversations.router,
    tags=["conversations"],
)


# ================================================================
# Reports
# ================================================================

api_router.include_router(
    reports.router,
    tags=["reports"],
)


# ================================================================
# Documents
# ================================================================

api_router.include_router(
    documents.router,
    tags=["documents"],
)