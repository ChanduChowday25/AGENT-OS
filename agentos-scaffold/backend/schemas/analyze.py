"""
Request/response schemas for POST /api/v1/analyze
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel


class AnalyzeRequest(BaseModel):

    file_id: str

    instructions: Optional[str] = None


class AnalyzeResponse(BaseModel):

    file_id: str

    status: str

    result: Optional[Dict[str, Any]] = None