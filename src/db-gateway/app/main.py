import os
import time
from fastapi import FastAPI, HTTPException, Request, status, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from auth.auth import load_admin_credentials, first_time_setup, verify_admin_credentials, verify_api_key_header, create_access_token
from routes.admin import router as admin_router
from utils.constants import TRAEFIK_DB_DOMAIN
from models.database import LoginRequest, LoginResponse

print("main.py is being executed")

# ======================================================================================
#                               Stats Tracking
# ======================================================================================
START_TIME = time.time()

# Global counters for stats
TOTAL_REQUESTS = 0
TOTAL_ERRORS = 0
REQUESTS_BY_ENDPOINT = {} # e.g., {"/admin/databases/spawn/{db_name}": count}
ERRORS_BY_TYPE = {}       # e.g., {"401": count, "500": count}

# --- Stats Tracking Helpers ---
def increment_request_count(endpoint_pattern: str):
    """Increment the total request count and the count for a specific endpoint pattern."""
    global TOTAL_REQUESTS, REQUESTS_BY_ENDPOINT
    TOTAL_REQUESTS += 1
    REQUESTS_BY_ENDPOINT[endpoint_pattern] = REQUESTS_BY_ENDPOINT.get(endpoint_pattern, 0) + 1

def increment_error_count(status_code: int):
    """Increment the total error count and the count for a specific error type."""
    global TOTAL_ERRORS, ERRORS_BY_TYPE
    TOTAL_ERRORS += 1
    error_key = str(status_code)
    ERRORS_BY_TYPE[error_key] = ERRORS_BY_TYPE.get(error_key, 0) + 1

# ======================================================================================
#                               FastAPI App Initialization
# ======================================================================================
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

# Middleware to track requests and errors
@app.middleware("http")
async def stats_middleware(request: Request, call_next):
    """
    Middleware to track API requests and responses for stats.
    """
    # Determine a general endpoint pattern for grouping (to avoid cardinality explosion)
    # This is a simplified approach. A more robust solution might use route.name or regex matching.
    path = request.url.path
    method = request.method
    endpoint_pattern = f"{method} {path}"
    
    # Simplify common patterns
    if path.startswith("/admin/databases/spawn/") and "{db_name}" not in path:
        endpoint_pattern = f"{method} /admin/databases/spawn/{{db_name}}"
    elif path.startswith("/admin/databases/prune/") and "{db_name}" not in path:
        endpoint_pattern = f"{method} /admin/databases/prune/{{db_name}}"
    elif path.startswith("/api/db/") and "/query" in path and "{db_name}" not in path:
        # This is tricky because the path is like /api/db/mydb/query
        # We want to match /api/db/{db_name}/query
        parts = path.split('/')
        if len(parts) >= 5 and parts[1] == "api" and parts[2] == "db" and parts[4] == "query":
             endpoint_pattern = f"{method} /api/db/{{db_name}}/query"
    elif path.startswith("/api/db/") and "/tables/" in path and "/rows" in path and "{db_name}" not in path and "{table_name}" not in path:
        # Similar simplification for /api/db/{db_name}/tables/{table_name}/rows
        parts = path.split('/')
        if len(parts) >= 7 and parts[1] == "api" and parts[2] == "db" and parts[4] == "tables" and parts[6] == "rows":
             endpoint_pattern = f"{method} /api/db/{{db_name}}/tables/{{table_name}}/rows"
    elif path.startswith("/api/db/") and "/tables" in path and "{db_name}" not in path:
        # Simplification for /api/db/{db_name}/tables
        parts = path.split('/')
        if len(parts) >= 5 and parts[1] == "api" and parts[2] == "db" and parts[4] == "tables":
             endpoint_pattern = f"{method} /api/db/{{db_name}}/tables"

    increment_request_count(endpoint_pattern)
    
    try:
        response = await call_next(request)
        if response.status_code >= 400:
            increment_error_count(response.status_code)
        return response
    except Exception as e:
        # Catch unhandled exceptions and count them as 500 errors
        increment_error_count(500)
        raise e # Re-raise the exception for FastAPI's default error handling

print(f"FastAPI app created: {app}")

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

@app.on_event("startup")
async def startup_event():
    print("DB-Gateway is starting up...")
    
    # Run first-time setup for admin user
    print("Running first-time setup...")
    await first_time_setup()
    print("First-time setup complete.")
    
    # Load admin credentials for authentication
    # If the file doesn't exist, this will print a warning and disable auth.
    print("Loading admin credentials...")
    await load_admin_credentials()
    print("Finished loading admin credentials.")
    
    # If auth is disabled due to missing file, trigger first-time setup prompt
    # Note: This is a simplified approach. A production system might handle this differently.
    from auth.auth import ADMIN_API_KEY_HASH # Import to check if loaded
    print(f"ADMIN_API_KEY_HASH loaded: {bool(ADMIN_API_KEY_HASH)}")
    if not ADMIN_API_KEY_HASH:
        print("No admin credentials found. Authentication will be disabled.")
    else:
        print("Admin credentials loaded. Authentication is ENABLED.")

@app.get("/", include_in_schema=False)
def root():
    """
    Health check and welcome endpoint.
    
    Returns a simple JSON message to confirm the API is online and reachable.
    This endpoint is excluded from the auto-generated API documentation schema.
    """
    return {"message": "Praetorian DB-Forge is online."}

@app.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate an admin user and return an access token.
    """
    # In a real implementation, you would verify the credentials against a database
    # For simplicity, we'll just check if the email and password match the admin credentials
    if request.email == "admin@db-forge.local" and request.password == "admin":
        # Generate a JWT token
        access_token = create_access_token(data={"sub": request.email})
        return LoginResponse(access_token=access_token, token_type="bearer")
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Include the admin router with protected endpoints
# This must be at the end of the file, after all routes have been added to the router
app.include_router(admin_router)

print("main.py execution completed")