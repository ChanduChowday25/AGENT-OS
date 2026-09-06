"""ORM model for the `generated_reports` table (SAS section 10)."""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func

from models.base import Base


class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    format = Column(String, nullable=False)  # "pdf" | "docx"
    storage_path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
