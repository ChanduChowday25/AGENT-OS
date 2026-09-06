"""ORM model for the `uploaded_files` table (SAS section 10)."""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func

from models.base import Base


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=True)
    storage_path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
