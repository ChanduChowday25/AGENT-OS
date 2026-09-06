"""Response schemas for GET /api/v1/reports"""

from typing import List
from pydantic import BaseModel


class ReportSummary(BaseModel):
    report_id: str
    filename: str
    format: str  # "pdf" | "docx"
    created_at: str


class ReportListResponse(BaseModel):
    reports: List[ReportSummary]
