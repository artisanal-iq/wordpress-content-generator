class AgentError(Exception):
    """Base class for agent-related exceptions."""


class AgentConfigError(AgentError):
    """Raised when required configuration is missing."""


class AgentDataError(AgentError):
    """Raised when expected data is missing or retrieval fails."""
