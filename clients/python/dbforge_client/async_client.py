"""Asynchronous DB-Forge client implementation."""

import asyncio
import os
from typing import Dict, Any, List, Optional

import aiohttp
from aiohttp import ClientSession, ClientTimeout

from .exceptions import (
    DBForgeError,
    DatabaseNotFound,
    InvalidRequest,
    AuthenticationError,
    ServerError,
    ConnectionError,
    TimeoutError,
)


class AsyncDBForgeDatabase:
    """Async database-specific operations wrapper."""
    
    def __init__(self, client: "AsyncDBForgeClient", name: str):
        """Initialize async database wrapper.
        
        Args:
            client: AsyncDBForgeClient instance
            name: Database name
        """
        self.client = client
        self.name = name
    
    async def create_table(self, table_name: str, columns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a new table in the database."""
        data = {
            "table_name": table_name,
            "columns": columns
        }
        return await self.client._make_request("POST", f"/api/db/{self.name}/tables", json_data=data)
    
    async def insert_rows(self, table_name: str, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Insert rows into a table."""
        data = {"rows": rows}
        return await self.client._make_request(
            "POST", 
            f"/api/db/{self.name}/tables/{table_name}/rows",
            json_data=data
        )
    
    async def select_rows(
        self, 
        table_name: str, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Select rows from a table with optional filtering."""
        params = filters or {}
        response = await self.client._make_request(
            "GET",
            f"/api/db/{self.name}/tables/{table_name}/rows",
            params=params
        )
        return response.get("data", [])
    
    async def execute_query(
        self, 
        sql: str, 
        params: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """Execute raw SQL query against the database."""
        data = {"sql": sql}
        if params:
            data["params"] = params
        
        return await self.client._make_request("POST", f"/api/db/{self.name}/query", json_data=data)


class AsyncDBForgeClient:
    """Main asynchronous client for DB-Forge operations."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30,
        connector_limit: int = 20,
    ):
        """Initialize async DB-Forge client.
        
        Args:
            base_url: Base URL for DB-Forge server
            api_key: API key for authentication
            timeout: Request timeout in seconds
            connector_limit: Maximum number of connections
        """
        self.base_url = base_url or os.getenv("DBFORGE_BASE_URL", "http://db.localhost")
        self.api_key = api_key or os.getenv("DBFORGE_API_KEY")
        self.timeout = ClientTimeout(total=timeout)
        
        # Session will be created when needed
        self._session: Optional[ClientSession] = None
        self.connector_limit = connector_limit
        
        # Default headers
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "DBForge-Python-AsyncClient/1.0.0",
        }
        
        if self.api_key:
            self.headers["X-API-Key"] = self.api_key
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure session is created."""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(limit=self.connector_limit)
            self._session = ClientSession(
                connector=connector,
                timeout=self.timeout,
                headers=self.headers
            )
    
    async def close(self):
        """Close the client session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make async HTTP request to DB-Forge server."""
        await self._ensure_session()
        
        url = self.base_url.rstrip("/") + endpoint
        
        try:
            async with self._session.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
            ) as response:
                
                # Handle different response types
                try:
                    response_data = await response.json()
                except ValueError:
                    text = await response.text()
                    response_data = {"message": text}
                
                # Check for errors
                if not response.ok:
                    error_info = response_data.get("error", {})
                    message = error_info.get("message", f"HTTP {response.status}")
                    error_code = error_info.get("code")
                    
                    if response.status == 404:
                        raise DatabaseNotFound(message, response.status, error_code, response_data)
                    elif response.status == 400:
                        raise InvalidRequest(message, response.status, error_code, response_data)
                    elif response.status == 401:
                        raise AuthenticationError(message, response.status, error_code, response_data)
                    elif response.status >= 500:
                        raise ServerError(message, response.status, error_code, response_data)
                    else:
                        raise DBForgeError(message, response.status, error_code, response_data)
                
                return response_data
                
        except aiohttp.ClientConnectionError as e:
            raise ConnectionError(f"Failed to connect to DB-Forge server: {e}")
        except asyncio.TimeoutError as e:
            raise TimeoutError(f"Request timed out: {e}")
        except aiohttp.ClientError as e:
            raise DBForgeError(f"Request failed: {e}")
    
    # Admin API methods
    
    async def spawn_database(self, name: str) -> Dict[str, Any]:
        """Spawn a new database instance."""
        return await self._make_request("POST", f"/admin/databases/spawn/{name}")
    
    async def prune_database(self, name: str) -> Dict[str, Any]:
        """Prune (remove) a database instance."""
        return await self._make_request("POST", f"/admin/databases/prune/{name}")
    
    async def list_databases(self) -> List[Dict[str, Any]]:
        """List all active database instances."""
        return await self._make_request("GET", "/admin/databases")
    
    # Database operations
    
    def get_database(self, name: str) -> AsyncDBForgeDatabase:
        """Get a database instance for operations."""
        return AsyncDBForgeDatabase(self, name)
    
    # Health check
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the DB-Forge server is healthy."""
        return await self._make_request("GET", "/")