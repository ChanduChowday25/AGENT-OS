"""
Memory Service (SAS section 8) — conversation/task history.
Deliberately NOT an LLM-driven agent: plain read/write against SQLite.
"""

import uuid

from sqlalchemy.orm import Session

from models.conversation import Conversation
from models.message import Message


class MemoryService:
    def __init__(self, db: Session):
        self.db = db

    def get_conversation_title(self, conversation_id: str, title: str | None = None):
        if title and title.strip():
            return title

        first_user_message = (
            self.db.query(Message)
            .filter(
                Message.conversation_id == conversation_id,
                Message.role == "user",
            )
            .order_by(Message.created_at.asc(), Message.id.asc())
            .first()
        )

        if first_user_message is None:
            return title

        return first_user_message.content[:80].strip()

    def get_conversation_history(self, conversation_id: str):
        return (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc(), Message.id.asc())
            .all()
        )

    def list_conversations(self):
        return (
            self.db.query(Conversation)
            .order_by(Conversation.created_at.desc(), Conversation.id.desc())
            .all()
        )

    def get_conversation(self, conversation_id: str):
        return (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )

    def delete_conversation(self, conversation_id: str):
        conversation = self.get_conversation(conversation_id)

        if conversation is None:
            return False

        messages = (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .all()
        )

        for message in messages:
            self.db.delete(message)

        self.db.delete(conversation)
        self.db.commit()

        return True

    def create_conversation_if_missing(self, conversation_id: str):
        conversation = self.get_conversation(conversation_id)

        if conversation is None:
            conversation = Conversation(id=conversation_id)
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)

        return conversation

    def save_message(self, conversation_id: str, role: str, content: str):
        message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message