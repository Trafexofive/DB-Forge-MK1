import os
import re
import docker
import aiosqlite
from fastapi import FastAPI, HTTPException, Request, status, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware # Import for CORS
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
# Import our new auth module
from auth import load_admin_credentials, first_time_setup_prompt, verify_api_key_header

# ... (rest of the imports and config)

# ======================================================================================
#                               Configuration
# ======================================================================================
# Load configuration from environment variables
TRAEFIK_DB_DOMAIN = os.getenv("TRAEFIK_DB_DOMAIN", "db.localhost")
CHIMERA_NETWORK = os.getenv("CHIMERA_NETWORK", "db-forge-net")
DB_WORKER_IMAGE = os.getenv("DB_WORKER_IMAGE", "db-worker-base:latest")
DB_DATA_PATH = "/databases"

# Initialize Docker client
try:
    docker_client = docker.from_env()
except docker.errors.DockerException:
    print("Error: Could not connect to Docker daemon. Is it running?")
    docker_client = None

# Initialize FastAPI app
app = FastAPI(
    title="Praetorian DB-Forge",
    description=(
        "A containerized, RESTful database-as-a-service gateway. "
        "DB-Forge allows you to dynamically spawn, manage, and interact with "
        "isolated SQLite database instances. It's designed for ephemeral data storage, "
        "testing, and as a lightweight DB hub for other services. "
        "All data is stored on the host filesystem for absolute sovereignty."
    ),
    version="1.0.0",
    # Adding contact and license info can be good for formal APIs
    contact={
        "name": "Gemini (Master Systems Consultant)",
        "url": "https://github.com/Praetorian-DB-Forge", # Placeholder URL
    },
    license_info={
        "name": "MIT License",
        "url": "https://github.com/Praetorian-DB-Forge/LICENSE", # Placeholder URL
    },
)

# Create a dedicated router for admin endpoints, protected by API key auth
admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(verify_api_key_header)] # Apply auth dependency to all routes in this router
)

# Configure CORS for frontend integration (Development settings)
# IMPORTANT: Review and tighten these settings for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permissive for development. Use specific origins in production.
    allow_credentials=True,
    allow_methods=["*"], # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"], # Allow all headers
    # expose_headers=["Access-Control-Allow-Origin"] # Optional: Expose specific headers to the browser
)

# Include the admin router with protected endpoints
app.include_router(admin_router)

# ======================================================================================
#                               Structured Error Handling
# ======================================================================================
class ErrorResponse(BaseModel):
    """
    Standardized error response format.
    
    All error responses from the API will follow this structure to provide consistency
    for clients.
    """
    error: Dict[str, Any] = Field(
        ...,
        example={
            "code": "NOT_FOUND",
            "message": "The requested resource was not found.",
            "status": 404
        },
        description=(
            "A dictionary containing error details. "
            "'code' is a machine-readable error identifier. "
            "'message' is a human-readable description. "
            "'status' is the corresponding HTTP status code. "
            "'details' may be included for additional context (not always present)."
        )
    )

class StructuredHTTPException(HTTPException):
    """Custom exception to carry structured error details."""
    def __init__(self, status_code: int, code: str, message: str, details: Optional[Any] = None):
        super().__init__(status_code=status_code, detail=message)
        self.code = code
        self.details = details

@app.exception_handler(StructuredHTTPException)
async def structured_exception_handler(request: Request, exc: StructuredHTTPException):
    """Handle StructuredHTTPException and return a standardized error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.detail,
                "status": exc.status_code,
                "details": exc.details
            }
        },
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle standard FastAPI HTTPException and wrap it in our standardized format."""
    # Map common FastAPI/HTTP status codes to our internal error codes
    code_map = {
        status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
        status.HTTP_404_NOT_FOUND: "NOT_FOUND",
        status.HTTP_409_CONFLICT: "CONFLICT",
        status.HTTP_503_SERVICE_UNAVAILABLE: "SERVICE_UNAVAILABLE",
        status.HTTP_422_UNPROCESSABLE_ENTITY: "VALIDATION_ERROR",
    }
    error_code = code_map.get(exc.status_code, "INTERNAL_ERROR")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": error_code,
                "message": exc.detail,
                "status": exc.status_code,
                # 'details' are not included for standard HTTPExceptions unless specifically added
            }
        },
    )

# ======================================================================================
#                               Pydantic Models
# ======================================================================================
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

# ======================================================================================
#                               Utility Functions
# ======================================================================================
def is_valid_db_name(db_name: str) -> bool:
    """Check if db_name is valid for filesystem and Docker container names."""
    return re.match(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]*$", db_name) is not None

def get_db_path(db_name: str) -> str:
    """Get the full path to the SQLite database file."""
    return os.path.join(DB_DATA_PATH, f"{db_name}.db")

def get_worker_name(db_name: str) -> str:
    """Get the conventional name for a worker container."""
    return f"db-worker-{db_name}"

async def db_file_exists(db_name: str) -> bool:
    """Check if the database file exists."""
    db_path = get_db_path(db_name)
    return os.path.exists(db_path)

# ======================================================================================
#                               Admin API (Orchestrator)
# ======================================================================================
@admin_router.post("/databases/spawn/{db_name}", response_model=SpawnResponse, status_code=status.HTTP_201_CREATED)
async def spawn_database(db_name: str):
    """
    Spawns a new, isolated database instance.
    
    This endpoint creates a new Docker container running a `db-worker` image, 
    which holds an SQLite database file. If an instance with the given name 
    already exists and is running, the request is idempotent and will return 
    a success message. If the instance exists but is stopped, it will be started.
    
    The database file is created on the host filesystem and mounted into the worker.
    This ensures data persists beyond the container lifecycle.
    
    Args:
        db_name (str): A unique name for the database. Must be filesystem and Docker-name friendly.
        
    Returns:
        SpawnResponse: Details about the spawned or existing database instance.
        
    Raises:
        HTTPException:
            - 400: If the `db_name` is invalid.
            - 503: If the Docker daemon is not available.
    """
    if not is_valid_db_name(db_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid database name.")
    if not docker_client:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Docker not available.")

    worker_name = get_worker_name(db_name)
    try:
        container = docker_client.containers.get(worker_name)
        if container.status == "exited":
            container.start()
        return SpawnResponse(
            message="Database instance already exists and is running.",
            db_name=db_name,
            container_id=container.id,
        )
    except docker.errors.NotFound:
        # Create DB file placeholder
        db_path = get_db_path(db_name)
        if not os.path.exists(DB_DATA_PATH):
            os.makedirs(DB_DATA_PATH)
        open(db_path, 'a').close()

        # Spawn container
        container = docker_client.containers.run(
            image=DB_WORKER_IMAGE,
            name=worker_name,
            hostname=worker_name,
            detach=True,
            network=CHIMERA_NETWORK,
            labels={"db-worker": "true", "db-name": db_name},
            restart_policy={"Name": "unless-stopped"}
        )
        return SpawnResponse(
            message="Database instance spawned successfully.",
            db_name=db_name,
            container_id=container.id,
        )

@admin_router.post("/databases/prune/{db_name}", response_model=PruneResponse)
async def prune_database(db_name: str):
    """Stops and removes a specific database instance container."""
    if not docker_client:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Docker not available.")
    
    worker_name = get_worker_name(db_name)
    try:
        container = docker_client.containers.get(worker_name)
        container.stop()
        container.remove()
        return PruneResponse(message="Database instance pruned successfully.", db_name=db_name)
    except docker.errors.NotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database instance not found.")

@admin_router.get("/databases", response_model=List[DBInstance])
async def list_databases():
    """Lists all currently managed database instances."""
    if not docker_client:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Docker not available.")

    instances = []
    containers = docker_client.containers.list(all=True, filters={"label": "db-worker=true"})
    for c in containers:
        db_name = c.labels.get("db-name", "unknown")
        instances.append(DBInstance(name=db_name, container_id=c.id, status=c.status))
    return instances

# ======================================================================================
#                               Data Plane API
# ======================================================================================
@app.post("/api/db/{db_name}/query", response_model=QueryResponse)
async def execute_query(db_name: str, query: RawQueryRequest):
    """
    Executes a raw SQL query against the specified database.
    
    This is the most flexible endpoint for data interaction. It allows executing
    SELECT, INSERT, UPDATE, DELETE, and DDL statements. The query can be parameterized
    for safety.
    
    For SELECT queries, the result set is returned in the `data` field.
    For other queries, a success message and the number of rows affected are returned.
    
    Args:
        db_name (str): The name of the target database instance.
        query (RawQueryRequest): The SQL statement and optional parameters.
        
    Returns:
        QueryResponse: The result of the query execution.
        
    Raises:
        HTTPException:
            - 404: If the database `db_name` does not exist.
            - 400: If the SQL statement is invalid or causes an error.
    """
    if not await db_file_exists(db_name):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found.")
    
    db_path = get_db_path(db_name)
    try:
        async with aiosqlite.connect(db_path) as db:
            db.row_factory = aiosqlite.Row
            is_select = query.sql.strip().upper().startswith("SELECT")
            
            params = query.params if query.params is not None else []
            cursor = await db.execute(query.sql, params)
            
            if is_select:
                rows = await cursor.fetchall()
                data = [dict(row) for row in rows]
                return QueryResponse(data=data, rows_affected=len(data))
            else:
                await db.commit()
                return QueryResponse(
                    message="Query executed successfully.",
                    rows_affected=cursor.rowcount
                )
    except aiosqlite.Error as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"SQL Error: {e}")

@app.post("/api/db/{db_name}/tables", response_model=CreateTableResponse, status_code=status.HTTP_201_CREATED)
async def create_table(db_name: str, req: CreateTableRequest):
    """Creates a new table in the specified database."""
    if not await db_file_exists(db_name):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found.")

    cols_defs = []
    for col in req.columns:
        col_str = f"'{col.name}' {col.type}"
        if col.primary_key:
            col_str += " PRIMARY KEY"
        if col.not_null:
            col_str += " NOT NULL"
        if col.default is not None:
            default_val = f"'{col.default}'" if isinstance(col.default, str) else col.default
            col_str += f" DEFAULT {default_val}"
        cols_defs.append(col_str)
    
    sql = f"CREATE TABLE IF NOT EXISTS '{req.table_name}' ({', '.join(cols_defs)})"
    
    db_path = get_db_path(db_name)
    try:
        async with aiosqlite.connect(db_path) as db:
            await db.execute(sql)
            await db.commit()
        return CreateTableResponse(message=f"Table '{req.table_name}' created successfully.")
    except aiosqlite.Error as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"SQL Error: {e}")

@app.get("/api/db/{db_name}/tables/{table_name}/rows", response_model=QueryResponse)
async def get_rows(db_name: str, table_name: str, request: Request):
    """Selects rows from a table with simple key-value filtering."""
    if not await db_file_exists(db_name):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found.")

    filters = request.query_params
    sql = f"SELECT * FROM '{table_name}'"
    params = []
    if filters:
        where_clauses = []
        for key, value in filters.items():
            where_clauses.append(f"{key} = ?")
            params.append(value)
        sql += " WHERE " + " AND ".join(where_clauses)

    db_path = get_db_path(db_name)
    try:
        async with aiosqlite.connect(db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(sql, params)
            rows = await cursor.fetchall()
            data = [dict(row) for row in rows]
            return QueryResponse(data=data, rows_affected=len(data))
    except aiosqlite.Error as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"SQL Error: {e}")

@app.post("/api/db/{db_name}/tables/{table_name}/rows", response_model=InsertResponse, status_code=status.HTTP_201_CREATED)
async def insert_rows(db_name: str, table_name: str, req: InsertRequest):
    """Inserts one or more rows into a table."""
    if not await db_file_exists(db_name):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found.")
    if not req.rows:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No rows provided.")

    first_row = req.rows[0]
    columns = first_row.keys()
    col_names = ", ".join([f"'{c}'" for c in columns])
    placeholders = ", ".join(["?"] * len(columns))
    sql = f"INSERT INTO '{table_name}' ({col_names}) VALUES ({placeholders})"
    
    params = [tuple(row.get(col) for col in columns) for row in req.rows]

    db_path = get_db_path(db_name)
    try:
        async with aiosqlite.connect(db_path) as db:
            await db.executemany(sql, params)
            await db.commit()
        return InsertResponse(message="Rows inserted successfully.", rows_affected=len(req.rows))
    except aiosqlite.Error as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"SQL Error: {e}")

@app.on_event("startup")
async def startup_event():
    # This is just to confirm docker_client is available on startup
    if not docker_client:
        print("WARNING: Docker client is not available. Admin functions will fail.")
    
    # Load admin credentials for authentication
    # If the file doesn't exist, this will print a warning and disable auth.
    await load_admin_credentials()
    
    # If auth is disabled due to missing file, trigger first-time setup prompt
    # Note: This is a simplified approach. A production system might handle this differently.
    from auth import ADMIN_API_KEY_HASH # Import to check if loaded
    if not ADMIN_API_KEY_HASH:
        print("No admin credentials found. Initiating first-time setup...")
        await first_time_setup_prompt()
        print("Setup complete. Please restart the service to load the new credentials.")
        # Optionally, you could raise an exception to stop the app here
        # raise RuntimeError("Initial setup required. Please restart after setup.")

@app.get("/", include_in_schema=False)
def root():
    """
    Health check and welcome endpoint.
    
    Returns a simple JSON message to confirm the API is online and reachable.
    This endpoint is excluded from the auto-generated API documentation schema.
    """
    return {"message": "Praetorian DB-Forge is online."}
