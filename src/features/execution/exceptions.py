from __future__ import annotations


class ExecutionServiceError(Exception):
    """Base exception for execution service errors."""
    pass


class ContextBuildError(ExecutionServiceError):
    """Raised when context building fails."""
    pass


class ContextNotFoundError(ExecutionServiceError):
    """Raised when requested context doesn't exist."""
    pass