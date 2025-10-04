"""Synchronous DB-Forge client implementation."""

import os
import time
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import (
    DBForgeError,
    DatabaseNotFound,
    InvalidRequest,
    AuthenticationError,
    ServerError,
    ConnectionError,
    TimeoutError,
)
from .database import DBForgeDatabase


class DBForgeClient:
    """Main synchronous client for DB-Forge operations."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30,
        retries: int = 3,
        backoff_factor: float = 0.3,
    ):
        """Initialize DB-Forge client.
        
        Args:
            base_url: Base URL for DB-Forge server (default: http://db.localhost)
            api_key: API key for authentication (optional)
            timeout: Request timeout in seconds
            retries: Number of retry attempts for failed requests
            backoff_factor: Backoff factor for retries
        """
        self.base_url = base_url or os.getenv("DBFORGE_BASE_URL", "http://db.localhost")
        self.api_key = api_key or os.getenv("DBFORGE_API_KEY")
        self.timeout = timeout
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "DBForge-Python-Client/1.0.0",
        })
        
        if self.api_key:
            self.session.headers["X-API-Key"] = self.api_key
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to DB-Forge server.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            json_data: JSON data to send in request body
            params: URL parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            DBForgeError: On API errors
            ConnectionError: On connection issues
            TimeoutError: On timeout
        """
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                timeout=self.timeout,
            )
            
            # Handle different response types
            try:
                response_data = response.json()
            except ValueError:
                response_data = {"message": response.text}
            
            # Check for errors
            if not response.ok:
                error_info = response_data.get("error", {})
                message = error_info.get("message", f"HTTP {response.status_code}")
                error_code = error_info.get("code")
                
                if response.status_code == 404:
                    raise DatabaseNotFound(message, response.status_code, error_code, response_data)
                elif response.status_code == 400:
                    raise InvalidRequest(message, response.status_code, error_code, response_data)
                elif response.status_code == 401:
                    raise AuthenticationError(message, response.status_code, error_code, response_data)
                elif response.status_code >= 500:
                    raise ServerError(message, response.status_code, error_code, response_data)
                else:
                    raise DBForgeError(message, response.status_code, error_code, response_data)
            
            return response_data
            
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to DB-Forge server: {e}")
        except requests.exceptions.Timeout as e:
            raise TimeoutError(f"Request timed out: {e}")
        except requests.exceptions.RequestException as e:
            raise DBForgeError(f"Request failed: {e}")
    
    # Admin API methods
    
    def spawn_database(self, name: str) -> Dict[str, Any]:
        """Spawn a new database instance.
        
        Args:
            name: Database name
            
        Returns:
            Response data containing database info
        """
        return self._make_request("POST", f"/admin/databases/spawn/{name}")
    
    def prune_database(self, name: str) -> Dict[str, Any]:
        """Prune (remove) a database instance.
        
        Args:
            name: Database name
            
        Returns:
            Response data
        """
        return self._make_request("POST", f"/admin/databases/prune/{name}")
    
    def list_databases(self) -> List[Dict[str, Any]]:
        """List all active database instances.
        
        Returns:
            List of database information
        """
        return self._make_request("GET", "/admin/databases")
    
    # Database operations
    
    def get_database(self, name: str) -> DBForgeDatabase:
        """Get a database instance for operations.
        
        Args:
            name: Database name
            
        Returns:
            DBForgeDatabase instance
        """
        return DBForgeDatabase(self, name)
    
    # Health check
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the DB-Forge server is healthy.
        
        Returns:
            Health check response
        """
        return self._make_request("GET", "/")