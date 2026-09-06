"""GET /api/v1/conversations — controller only."""

from fastapi import APIRouter

from schemas.conversation import ConversationListResponse

router = APIRouter()


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations():
    """TODO: call services.memory_service to list conversations."""
    raise NotImplementedError
