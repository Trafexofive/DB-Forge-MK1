"""
Async API client for DB-Forge server communication
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import aiohttp
from aiohttp import ClientError, ClientTimeout

from ..config import Config


class DBForgeAPIClient:
    """Asynchronous API client for DB-Forge server."""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.server.url
        self.timeout = ClientTimeout(total=config.server.timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Headers
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "DBForge-TUI/1.0.0"
        }
        
        if config.server.api_key:
            self.headers["X-API-Key"] = config.server.api_key
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self) -> None:
        """Ensure aiohttp session is created."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers=self.headers
            )
    
    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to DB-Forge server."""
        
        await self._ensure_session()
        
        url = urljoin(self.base_url, endpoint)
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                params=params
            ) as response:
                
                # Parse response
                try:
                    response_data = await response.json()
                except Exception:
                    response_data = {"message": await response.text()}
                
                # Check for errors
                if not response.ok:
                    error_info = response_data.get("error", {})
                    message = error_info.get("message", f"HTTP {response.status}")
                    raise DBForgeAPIError(message, response.status, response_data)
                
                return response_data
                
        except ClientError as e:
            raise DBForgeAPIError(f"Connection error: {str(e)}")
        except asyncio.TimeoutError:
            raise DBForgeAPIError("Request timed out")
    
    # Health and status
    
    async def health_check(self) -> Dict[str, Any]:
        """Check server health status."""
        try:
            return await self._request("GET", "/")
        except DBForgeAPIError:
            return {"status": "error", "message": "Server unreachable"}
    
    # Database management (Admin API)
    
    async def list_databases(self) -> List[Dict[str, Any]]:
        """List all database instances."""
        return await self._request("GET", "/admin/databases")
    
    async def spawn_database(self, name: str) -> Dict[str, Any]:
        """Create a new database instance."""
        return await self._request("POST", f"/admin/databases/spawn/{name}")
    
    async def prune_database(self, name: str) -> Dict[str, Any]:
        """Remove a database instance."""
        return await self._request("POST", f"/admin/databases/prune/{name}")
    
    # Database operations (Data API)
    
    async def execute_query(
        self, 
        db_name: str, 
        sql: str, 
        params: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """Execute SQL query against database."""
        
        data = {"sql": sql}
        if params:
            data["params"] = params
        
        return await self._request("POST", f"/api/db/{db_name}/query", data)
    
    async def create_table(
        self, 
        db_name: str, 
        table_name: str, 
        columns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create a table in database."""
        
        data = {
            "table_name": table_name,
            "columns": columns
        }
        
        return await self._request("POST", f"/api/db/{db_name}/tables", data)
    
    async def insert_rows(
        self, 
        db_name: str, 
        table_name: str, 
        rows: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Insert rows into table."""
        
        data = {"rows": rows}
        
        return await self._request(
            "POST", 
            f"/api/db/{db_name}/tables/{table_name}/rows", 
            data
        )
    
    async def select_rows(
        self, 
        db_name: str, 
        table_name: str, 
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Select rows from table."""
        
        return await self._request(
            "GET",
            f"/api/db/{db_name}/tables/{table_name}/rows",
            params=filters or {}
        )
    
    # Utility methods
    
    async def get_database_schema(self, db_name: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get complete database schema."""
        
        # Get all tables
        tables_result = await self.execute_query(
            db_name,
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        
        schema = {}
        tables = tables_result.get("data", [])
        
        # Get columns for each table
        for table_row in tables:
            table_name = table_row["name"]
            
            columns_result = await self.execute_query(
                db_name,
                f"PRAGMA table_info({table_name})"
            )
            
            schema[table_name] = columns_result.get("data", [])
        
        return schema
    
    async def get_database_stats(self, db_name: str) -> Dict[str, Any]:
        """Get database statistics."""
        
        try:
            # Get table count
            table_count_result = await self.execute_query(
                db_name,
                "SELECT COUNT(name) as table_count FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            table_count = table_count_result.get("data", [{}])[0].get("table_count", 0)
            
            # Get database size
            size_result = await self.execute_query(
                db_name,
                "SELECT page_count * page_size as size_bytes FROM pragma_page_count(), pragma_page_size()"
            )
            size_bytes = size_result.get("data", [{}])[0].get("size_bytes", 0)
            
            return {
                "table_count": table_count,
                "size_bytes": size_bytes,
                "size_mb": round(size_bytes / (1024 * 1024), 2) if size_bytes else 0
            }
            
        except Exception:
            return {
                "table_count": 0,
                "size_bytes": 0,
                "size_mb": 0,
                "error": "Could not retrieve stats"
            }
    
    async def explain_query(self, db_name: str, sql: str) -> List[Dict[str, Any]]:
        """Get query execution plan."""
        
        result = await self.execute_query(db_name, f"EXPLAIN QUERY PLAN {sql}")
        return result.get("data", [])


class DBForgeAPIError(Exception):
    """Exception raised for API errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None, 
        response_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}


# Query metrics tracking
class QueryMetrics:
    """Track query performance metrics."""
    
    def __init__(self):
        self.total_queries = 0
        self.total_time = 0
        self.slow_queries = []
        self.recent_queries = []
        self.max_history = 100
    
    def add_query(
        self, 
        sql: str, 
        duration_ms: int, 
        success: bool = True,
        error: Optional[str] = None
    ) -> None:
        """Add query to metrics."""
        
        self.total_queries += 1
        
        query_record = {
            "sql": sql[:100] + "..." if len(sql) > 100 else sql,
            "duration_ms": duration_ms,
            "timestamp": datetime.now(),
            "success": success,
            "error": error
        }
        
        if success:
            self.total_time += duration_ms
            
            # Track slow queries (configurable threshold)
            if duration_ms > 1000:  # 1 second threshold
                self.slow_queries.append(query_record)
                if len(self.slow_queries) > 50:
                    self.slow_queries = self.slow_queries[-50:]
        
        # Add to recent queries
        self.recent_queries.insert(0, query_record)
        if len(self.recent_queries) > self.max_history:
            self.recent_queries = self.recent_queries[:self.max_history]
    
    @property
    def avg_response_time(self) -> float:
        """Calculate average response time for successful queries."""
        successful_queries = sum(1 for q in self.recent_queries if q["success"])
        if successful_queries == 0:
            return 0.0
        
        total_success_time = sum(
            q["duration_ms"] for q in self.recent_queries if q["success"]
        )
        
        return round(total_success_time / successful_queries, 1)
    
    @property
    def success_rate(self) -> float:
        """Calculate query success rate."""
        if not self.recent_queries:
            return 100.0
        
        successful = sum(1 for q in self.recent_queries if q["success"])
        return round((successful / len(self.recent_queries)) * 100, 1)