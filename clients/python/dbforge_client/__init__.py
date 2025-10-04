"""DB-Forge Python Client Library.

A comprehensive Python client for Praetorian DB-Forge that provides both
synchronous and asynchronous interfaces for database management and operations.
"""

from .client import DBForgeClient
from .async_client import AsyncDBForgeClient
from .database import DBForgeDatabase
from .exceptions import (
    DBForgeError,
    DatabaseNotFound,
    InvalidRequest,
    AuthenticationError,
    ServerError,
)

__version__ = "1.0.0"
__author__ = "Praetorian DB-Forge Team"
__email__ = "contact@dbforge.dev"

__all__ = [
    "DBForgeClient",
    "AsyncDBForgeClient",
    "DBForgeDatabase",
    "DBForgeError",
    "DatabaseNotFound",
    "InvalidRequest",
    "AuthenticationError",
    "ServerError",
]