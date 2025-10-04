"""Tests for DB-Forge Python client."""

import pytest
import json
from unittest.mock import Mock, patch
from dbforge_client import DBForgeClient, DBForgeError, DatabaseNotFound


class TestDBForgeClient:
    """Test cases for DBForgeClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = DBForgeClient(
            base_url="http://test.localhost",
            api_key="test-key"
        )
    
    @patch('requests.Session.request')
    def test_spawn_database_success(self, mock_request):
        """Test successful database spawn."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "message": "Database instance spawned successfully.",
            "db_name": "test-db",
            "container_id": "abc123"
        }
        mock_request.return_value = mock_response
        
        result = self.client.spawn_database("test-db")
        
        assert result["db_name"] == "test-db"
        assert result["container_id"] == "abc123"
        mock_request.assert_called_once()
    
    @patch('requests.Session.request')
    def test_spawn_database_error(self, mock_request):
        """Test database spawn with error."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {
                "code": "BAD_REQUEST",
                "message": "Invalid database name.",
                "status": 400
            }
        }
        mock_request.return_value = mock_response
        
        with pytest.raises(DBForgeError):
            self.client.spawn_database("invalid-db")
    
    @patch('requests.Session.request')
    def test_list_databases(self, mock_request):
        """Test listing databases."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = [
            {
                "name": "db1",
                "container_id": "abc123",
                "status": "running"
            },
            {
                "name": "db2", 
                "container_id": "def456",
                "status": "running"
            }
        ]
        mock_request.return_value = mock_response
        
        result = self.client.list_databases()
        
        assert len(result) == 2
        assert result[0]["name"] == "db1"
        assert result[1]["name"] == "db2"
    
    @patch('requests.Session.request')
    def test_database_not_found(self, mock_request):
        """Test database not found error."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "error": {
                "code": "NOT_FOUND",
                "message": "Database instance not found.",
                "status": 404
            }
        }
        mock_request.return_value = mock_response
        
        with pytest.raises(DatabaseNotFound):
            self.client.prune_database("nonexistent-db")
    
    def test_get_database(self):
        """Test getting database instance."""
        db = self.client.get_database("test-db")
        
        assert db.name == "test-db"
        assert db.client == self.client


class TestDBForgeDatabase:
    """Test cases for DBForgeDatabase."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = DBForgeClient(base_url="http://test.localhost")
        self.db = self.client.get_database("test-db")
    
    @patch('requests.Session.request')
    def test_create_table(self, mock_request):
        """Test table creation."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "message": "Table 'users' created successfully."
        }
        mock_request.return_value = mock_response
        
        columns = [
            {"name": "id", "type": "INTEGER", "primary_key": True},
            {"name": "username", "type": "TEXT", "not_null": True}
        ]
        
        result = self.db.create_table("users", columns)
        
        assert "created successfully" in result["message"]
        
        # Verify the request was made correctly
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "POST"
        assert "/api/db/test-db/tables" in call_args[1]["url"]
    
    @patch('requests.Session.request')
    def test_insert_rows(self, mock_request):
        """Test row insertion."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "message": "Rows inserted successfully.",
            "rows_affected": 2
        }
        mock_request.return_value = mock_response
        
        rows = [
            {"username": "alice", "email": "alice@example.com"},
            {"username": "bob", "email": "bob@example.com"}
        ]
        
        result = self.db.insert_rows("users", rows)
        
        assert result["rows_affected"] == 2
    
    @patch('requests.Session.request')
    def test_select_rows(self, mock_request):
        """Test row selection."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "data": [
                {"id": 1, "username": "alice", "email": "alice@example.com"}
            ],
            "rows_affected": 1
        }
        mock_request.return_value = mock_response
        
        result = self.db.select_rows("users", {"username": "alice"})
        
        assert len(result) == 1
        assert result[0]["username"] == "alice"
    
    @patch('requests.Session.request')
    def test_execute_query(self, mock_request):
        """Test raw query execution."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "data": [{"count": 5}],
            "rows_affected": 1
        }
        mock_request.return_value = mock_response
        
        result = self.db.execute_query("SELECT COUNT(*) as count FROM users")
        
        assert result["data"][0]["count"] == 5


if __name__ == "__main__":
    pytest.main([__file__])