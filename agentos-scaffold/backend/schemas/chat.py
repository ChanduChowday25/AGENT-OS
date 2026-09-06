"""
Request/response schemas for POST /api/v1/chat
"""

from typing import List, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):

    query: str

    conversation_id: str | None = None

    uploaded_file_ids: List[str] = []


class ChatResponse(BaseModel):

    conversation_id: str

    final_response: str

    workflow_trace: list = []