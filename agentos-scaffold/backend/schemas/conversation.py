"""Response schemas for GET /api/v1/conversations"""

from typing import List
from pydantic import BaseModel


class ConversationSummary(BaseModel):
    conversation_id: str
    title: str
    created_at: str


class ConversationListResponse(BaseModel):
    conversations: List[ConversationSummary]
