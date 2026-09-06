"""GET /api/v1/health"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "agentos-backend"}
