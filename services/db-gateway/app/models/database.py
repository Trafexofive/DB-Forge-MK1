from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class SpawnResponse(BaseModel):
    """
    Response model for spawning a database.
    
    Indicates the result of a request to create or ensure a database instance is running.
    """
    message: str = Field(
        ..., 
        example="Database instance spawned successfully.",
        description="A human-readable message describing the outcome."
    )
    db_name: str = Field(
        ..., 
        example="agent_memory_db",
        description="The name of the database instance."
    )
    container_id: Optional[str] = Field(
        None, 
        example="a1b2c3d4e5f6...",
        description="The Docker container ID if the instance was newly created or found."
    )

class PruneResponse(BaseModel):
    message: str
    db_name: str

class DBInstance(BaseModel):
    name: str
    container_id: str
    status: str

# --- New Models for Stats and Discovery ---

class GatewayStats(BaseModel):
    """
    Statistics for the DB-Gateway service itself.
    """
    uptime_seconds: float = Field(
        ..., 
        example=12345.67,
        description="Number of seconds the gateway has been running."
    )
    total_requests: int = Field(
        ..., 
        example=1234,
        description="Total number of HTTP requests received by the gateway."
    )
    total_errors: int = Field(
        ..., 
        example=5,
        description="Total number of HTTP errors (4xx, 5xx) returned by the gateway."
    )
    requests_by_endpoint: Dict[str, int] = Field(
        ..., 
        example={"/admin/databases/spawn/{db_name}": 100, "/api/db/{db_name}/query": 800},
        description="Breakdown of request counts by endpoint pattern."
    )
    errors_by_type: Dict[str, int] = Field(
        ..., 
        example={"401": 3, "500": 2},
        description="Breakdown of error counts by HTTP status code."
    )
    # Add more stats as needed, e.g., Docker API call stats, auth stats

class DiscoveryInfo(BaseModel):
    """
    Structured discovery information for a database instance.
    Useful for agents to programmatically find and connect.
    """
    db_name: str = Field(
        ..., 
        example="agent_memory_db",
        description="The name of the database instance."
    )
    status: str = Field(
        ..., 
        example="running",
        description="Current status of the database instance."
    )
    # Potentially add connection details, schema info snippets, etc. in the future

class RawQueryRequest(BaseModel):
    """
    Payload for executing a raw SQL query.
    
    Allows execution of any valid SQL statement against a database. 
    Use with caution. Parameterized queries are recommended to prevent injection.
    """
    sql: str = Field(
        ..., 
        example="SELECT * FROM users WHERE age > ?;",
        description="The SQL statement to execute."
    )
    params: Optional[List[Any]] = Field(
        None, 
        example=[25],
        description="A list of parameters to substitute into the SQL query."
    )

class QueryResponse(BaseModel):
    data: Optional[List[Dict[str, Any]]] = None
    rows_affected: int
    message: Optional[str] = None

class ColumnDefinition(BaseModel):
    name: str
    type: str
    primary_key: Optional[bool] = False
    not_null: Optional[bool] = False
    default: Optional[Any] = None

class CreateTableRequest(BaseModel):
    table_name: str
    columns: List[ColumnDefinition]

class CreateTableResponse(BaseModel):
    message: str

class InsertRequest(BaseModel):
    rows: List[Dict[str, Any]]

class InsertResponse(BaseModel):
    message: str
    rows_affected: int

# --- Authentication Models ---
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"