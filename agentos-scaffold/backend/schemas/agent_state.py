"""
AgentState — the single shared contract that flows through the
Supervisor and every specialized agent (SAS section 5).

Rules (per the frozen spec):
- The API layer creates the initial AgentState.
- The Supervisor owns routing and aggregation.
- Each agent may only write to the output field(s) it owns.
- No other object is used for inter-agent communication.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ExecutionPlan(BaseModel):
    """Structured plan produced by the Supervisor (SAS section 7)."""

    agents: List[str] = Field(default_factory=list)
    reason: str = ""


class WorkflowTraceEvent(BaseModel):
    """One step in the workflow — feeds the frontend visualization panel."""

    agent: str
    status: str  # "started" | "completed" | "failed"
    timestamp: Optional[str] = None
    detail: Optional[str] = None


class AgentState(BaseModel):
    # Input
    query: str
    uploaded_files: List[str] = Field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Supervisor
    execution_plan: Optional[ExecutionPlan] = None

    # Agent outputs — each agent updates only its own field
    research_output: Optional[Dict[str, Any]] = None
    rag_output: Optional[Dict[str, Any]] = None
    analytics_output: Optional[Dict[str, Any]] = None
    document_output: Optional[Dict[str, Any]] = None
    chat_output: Optional[Dict[str, Any]] = None

    # Workflow bookkeeping
    workflow_trace: List[WorkflowTraceEvent] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)

    # Output
    final_response: Optional[str] = None
    status: str = "pending"  # pending | running | completed | failed
