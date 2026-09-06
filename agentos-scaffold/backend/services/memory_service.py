"""
Memory Service (SAS section 8) — conversation/task history.
Deliberately NOT an LLM-driven agent: plain read/write against SQLite.
"""

from sqlalchemy.orm import Session


class MemoryService:
    def __init__(self, db: Session):
        self.db = db

    def get_conversation_history(self, conversation_id: str):
        # TODO: query the messages table for conversation_id
        raise NotImplementedError

    def save_message(self, conversation_id: str, role: str, content: str):
        # TODO: insert a row into the messages table
        raise NotImplementedError
