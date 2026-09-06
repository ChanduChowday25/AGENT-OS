"""ORM model for the `messages` table (SAS section 10)."""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from models.base import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
