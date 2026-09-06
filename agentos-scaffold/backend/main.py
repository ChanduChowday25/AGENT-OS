"""
AgentOS - FastAPI Application Entrypoint

Boots the FastAPI app, wires up CORS, includes the versioned API router.
No business logic lives here — see agents/, workflows/, services/.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import get_settings
from api.v1.router import api_router
from database.connection import init_db

settings = get_settings()

app = FastAPI(
    title="AgentOS API",
    description="Multi-Agent AI Orchestration Backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
def on_startup():
    init_db()
