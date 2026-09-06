"""
BaseAgent — the contract every specialized agent implements (SAS section 6).

Rules:
- Read AgentState.
- Update only the field(s) this agent owns.
- Return AgentState.
- Never call another agent directly — only the Supervisor may route.
"""

from abc import ABC, abstractmethod

from schemas.agent_state import AgentState


class BaseAgent(ABC):
    """Every agent (Research, RAG, Analytics, Document) extends this."""

    name: str = "base_agent"

    @abstractmethod
    def validate(self, state: AgentState) -> bool:
        """Check whether this agent has what it needs to run."""
        raise NotImplementedError

    @abstractmethod
    def execute(self, state: AgentState) -> AgentState:
        """Run the agent and return the updated AgentState."""
        raise NotImplementedError
