"""Database-specific operations for DB-Forge client."""

from typing import Dict, Any, List, Optional, TYPE_CHECKING
from urllib.parse import urlencode

if TYPE_CHECKING:
    from .client import DBForgeClient


class DBForgeDatabase:
    """Database-specific operations wrapper."""
    
    def __init__(self, client: "DBForgeClient", name: str):
        """Initialize database wrapper.
        
        Args:
            client: DBForgeClient instance
            name: Database name
        """
        self.client = client
        self.name = name
    
    def create_table(self, table_name: str, columns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a new table in the database.
        
        Args:
            table_name: Name of the table to create
            columns: List of column definitions
                Each column should be a dict with keys:
                - name: Column name
                - type: SQL data type (INTEGER, TEXT, REAL, BLOB)
                - primary_key: Boolean (optional)
                - not_null: Boolean (optional)
                - default: Default value (optional)
                - unique: Boolean (optional)
        
        Returns:
            Response data
            
        Example:
            db.create_table("users", [
                {"name": "id", "type": "INTEGER", "primary_key": True},
                {"name": "username", "type": "TEXT", "not_null": True, "unique": True},
                {"name": "email", "type": "TEXT", "not_null": True},
                {"name": "created_at", "type": "DATETIME", "default": "CURRENT_TIMESTAMP"}
            ])
        """
        data = {
            "table_name": table_name,
            "columns": columns
        }
        return self.client._make_request("POST", f"/api/db/{self.name}/tables", json_data=data)
    
    def insert_rows(self, table_name: str, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Insert rows into a table.
        
        Args:
            table_name: Name of the table
            rows: List of row data as dictionaries
        
        Returns:
            Response data with rows_affected count
            
        Example:
            db.insert_rows("users", [
                {"username": "alice", "email": "alice@example.com"},
                {"username": "bob", "email": "bob@example.com"}
            ])
        """
        data = {"rows": rows}
        return self.client._make_request(
            "POST", 
            f"/api/db/{self.name}/tables/{table_name}/rows",
            json_data=data
        )
    
    def select_rows(
        self, 
        table_name: str, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Select rows from a table with optional filtering.
        
        Args:
            table_name: Name of the table
            filters: Dictionary of column=value filters
        
        Returns:
            List of row data
            
        Example:
            # Get all rows
            rows = db.select_rows("users")
            
            # Get filtered rows
            active_users = db.select_rows("users", {"status": "active"})
        """
        params = filters or {}
        response = self.client._make_request(
            "GET",
            f"/api/db/{self.name}/tables/{table_name}/rows",
            params=params
        )
        return response.get("data", [])
    
    def execute_query(
        self, 
        sql: str, 
        params: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """Execute raw SQL query against the database.
        
        Args:
            sql: SQL query string
            params: Optional parameters for parameterized queries
        
        Returns:
            Query results
            
        Example:
            # Simple query
            result = db.execute_query("SELECT COUNT(*) as count FROM users")
            
            # Parameterized query
            result = db.execute_query(
                "SELECT * FROM users WHERE created_at > ? AND status = ?",
                ["2023-01-01", "active"]
            )
        """
        data = {"sql": sql}
        if params:
            data["params"] = params
        
        return self.client._make_request("POST", f"/api/db/{self.name}/query", json_data=data)
    
    def update_rows(
        self,
        table_name: str,
        set_values: Dict[str, Any],
        where_conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update rows in a table using SQL UPDATE.
        
        Args:
            table_name: Name of the table
            set_values: Dictionary of column=value pairs to update
            where_conditions: Dictionary of column=value conditions for WHERE clause
        
        Returns:
            Query results with rows_affected
            
        Example:
            db.update_rows(
                "users",
                {"status": "inactive", "updated_at": "CURRENT_TIMESTAMP"},
                {"last_login": "< 2023-01-01"}
            )
        """
        # Build UPDATE SQL
        set_clause = ", ".join([f"{col} = ?" for col in set_values.keys()])
        where_clause = " AND ".join([f"{col} = ?" for col in where_conditions.keys()])
        
        sql = f"UPDATE {table_name} SET {set_clause}"
        if where_clause:
            sql += f" WHERE {where_clause}"
        
        params = list(set_values.values()) + list(where_conditions.values())
        
        return self.execute_query(sql, params)
    
    def delete_rows(self, table_name: str, where_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Delete rows from a table.
        
        Args:
            table_name: Name of the table
            where_conditions: Dictionary of column=value conditions for WHERE clause
        
        Returns:
            Query results with rows_affected
            
        Example:
            db.delete_rows("users", {"status": "deleted"})
        """
        where_clause = " AND ".join([f"{col} = ?" for col in where_conditions.keys()])
        sql = f"DELETE FROM {table_name}"
        if where_clause:
            sql += f" WHERE {where_clause}"
        
        params = list(where_conditions.values())
        
        return self.execute_query(sql, params)
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get the schema information for a table.
        
        Args:
            table_name: Name of the table
        
        Returns:
            List of column information
        """
        result = self.execute_query(f"PRAGMA table_info({table_name})")
        return result.get("data", [])
    
    def list_tables(self) -> List[str]:
        """List all tables in the database.
        
        Returns:
            List of table names
        """
        result = self.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        return [row["name"] for row in result.get("data", [])]
    
    def drop_table(self, table_name: str) -> Dict[str, Any]:
        """Drop a table from the database.
        
        Args:
            table_name: Name of the table to drop
        
        Returns:
            Query results
        """
        return self.execute_query(f"DROP TABLE IF EXISTS {table_name}")