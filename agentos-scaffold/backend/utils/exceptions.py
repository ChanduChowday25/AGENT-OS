"""Shared exception types used across the backend."""


class AgentOSError(Exception):
    """Base exception for all AgentOS-specific errors."""


class AgentValidationError(AgentOSError):
    """Raised when an agent's validate() fails."""


class GeminiServiceError(AgentOSError):
    """Raised when the Gemini API call fails after the single retry
    (SAS section 14)."""
