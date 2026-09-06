"""
Schemas for structured analytics planning.

The Analytics Agent uses these models to represent
what the user wants to do with a dataset.

The LLM may produce an AnalysisPlan for complex
natural-language requests, but the actual dataset
processing is always performed locally using Pandas.
"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class FilterCondition(BaseModel):
    """
    Represents a single dataset filter.
    """
    column: str
    operator: str
    value: Any


class SortSpecification(BaseModel):
    """
    Represents sorting instructions.
    """
    column: Optional[str] = None
    direction: str = "asc"


class AnalysisPlan(BaseModel):
    """
    Structured representation of an analytical request.

    The plan describes WHAT should be done.
    It does not perform the actual analysis.
    Pandas/AnalyticsService will execute the plan.
    """
    operation: str
    aggregation: Optional[str] = None
    value_column: Optional[str] = None
    group_column: Optional[str] = None
    filters: List[FilterCondition] = Field(default_factory=list)
    sort: Optional[SortSpecification] = None
    limit: Optional[int] = None
    requested_info: Optional[str] = None