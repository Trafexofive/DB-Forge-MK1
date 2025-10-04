"""Custom exceptions for DB-Forge client."""

from typing import Optional, Dict, Any


class DBForgeError(Exception):
    """Base exception for all DB-Forge related errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.response_data = response_data or {}


class DatabaseNotFound(DBForgeError):
    """Raised when a database instance is not found."""
    pass


class InvalidRequest(DBForgeError):
    """Raised when the request is invalid (400 Bad Request)."""
    pass


class AuthenticationError(DBForgeError):
    """Raised when authentication fails (401 Unauthorized)."""
    pass


class ServerError(DBForgeError):
    """Raised when server encounters an error (5xx status codes)."""
    pass


class ConnectionError(DBForgeError):
    """Raised when unable to connect to DB-Forge server."""
    pass


class TimeoutError(DBForgeError):
    """Raised when request times out."""
    pass