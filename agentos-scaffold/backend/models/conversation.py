"""ORM model for the `conversations` table (SAS section 10)."""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func

from models.base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
