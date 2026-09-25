"""Conversation endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from models.conversation import Conversation
from schemas.conversation import ConversationListResponse, ConversationResponse
from services.memory_service import MemoryService

router = APIRouter()


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(db: Session = Depends(get_db)):
    memory_service = MemoryService(db)
    conversations = memory_service.list_conversations()

    return ConversationListResponse(
        conversations=[
            {
                "conversation_id": conversation.id,
                "title": memory_service.get_conversation_title(
                    conversation.id, conversation.title
                ),
                "created_at": conversation.created_at.isoformat(),
            }
            for conversation in conversations
        ]
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    memory_service = MemoryService(db)
    messages = memory_service.get_conversation_history(conversation_id)

    return ConversationResponse(
        conversation_id=conversation.id,
        title=memory_service.get_conversation_title(
            conversation.id, conversation.title
        ),
        created_at=conversation.created_at.isoformat(),
        messages=[
            {
                "message_id": message.id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
            }
            for message in messages
        ],
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
):
    deleted = MemoryService(db).delete_conversation(conversation_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    return {"conversation_id": conversation_id}
