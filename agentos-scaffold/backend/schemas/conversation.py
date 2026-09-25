"""Response schemas for conversation endpoints."""

from typing import List
from pydantic import BaseModel


class ConversationSummary(BaseModel):
    conversation_id: str
    title: str | None
    created_at: str


class ConversationListResponse(BaseModel):
    conversations: List[ConversationSummary]


class ConversationMessage(BaseModel):
    message_id: str
    role: str
    content: str
    created_at: str


class ConversationResponse(BaseModel):
    conversation_id: str
    title: str | None
    created_at: str
    messages: List[ConversationMessage]
