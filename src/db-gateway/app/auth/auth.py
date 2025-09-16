import os
import json
import secrets
import asyncio
from pathlib import Path
from passlib.context import CryptContext
from fastapi import HTTPException, status, Request, Depends
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
import aiosqlite

# --- Configuration ---
# Path to the file storing admin credentials (outside the container for persistence)
ADMIN_CREDS_FILE = Path(os.getenv("ADMIN_CREDS_PATH", "./secrets/admin.json"))
# Name of the HTTP header to expect the API key
API_KEY_HEADER_NAME = os.getenv("API_KEY_HEADER_NAME", "X-API-Key")
# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")  # In production, use a strong secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Password Hashing ---
# Using argon2 for password hashing (part of passlib[argon2])
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# --- API Key Handling ---
api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)

# --- In-Memory Storage ---
# To avoid reading the file on every request, we'll load the hashed key once.
# This assumes the key doesn't change during the app's lifetime without a restart.
# For a production system with key rotation, this would need to be more dynamic.
ADMIN_API_KEY_HASH: str = "" # This will be loaded at startup

# --- Configuration ---
# Path to the file storing admin credentials (outside the container for persistence)
ADMIN_CREDS_FILE = Path(os.getenv("ADMIN_CREDS_PATH", "./secrets/admin.json"))
# Name of the HTTP header to expect the API key
API_KEY_HEADER_NAME = os.getenv("API_KEY_HEADER_NAME", "X-API-Key")

# --- Password Hashing ---
# Using argon2 for password hashing (part of passlib[argon2])
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# --- API Key Handling ---
api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)

# --- In-Memory Storage ---
# To avoid reading the file on every request, we'll load the hashed key once.
# This assumes the key doesn't change during the app's lifetime without a restart.
# For a production system with key rotation, this would need to be more dynamic.
ADMIN_API_KEY_HASH: str = "" # This will be loaded at startup

def hash_api_key(api_key: str) -> str:
    """Hash an API key."""
    return pwd_context.hash(api_key)

def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    """Verify a plain API key against a hashed one."""
    return pwd_context.verify(plain_api_key, hashed_api_key)

def generate_secure_api_key() -> str:
    """Generate a cryptographically secure API key."""
    return secrets.token_urlsafe(32) # Generates a nice, long, random key

def create_access_token(data: dict):
    """Create a JWT access token."""
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def load_admin_credentials():
    """
    Load admin credentials from the file.
    This should be called once at application startup.
    """
    global ADMIN_API_KEY_HASH
    if not ADMIN_CREDS_FILE.exists():
        print(f"!!! WARNING !!! Admin credentials file not found: {ADMIN_CREDS_FILE}")
        print("                 Authentication will be disabled.")
        print("                 To enable auth, create the file or restart to trigger first-time setup.")
        return

    try:
        with open(ADMIN_CREDS_FILE, 'r') as f:
            data = json.load(f)
        
        if "password_hash" not in data:
             print(f"!!! ERROR !!! 'password_hash' not found in {ADMIN_CREDS_FILE}")
             print("                 Authentication will be disabled.")
             return

        ADMIN_API_KEY_HASH = data["password_hash"]
        print(f"Loaded admin credentials. Authentication is ENABLED.")
    except (json.JSONDecodeError, KeyError, IOError) as e:
        print(f"!!! ERROR !!! Failed to load admin credentials from {ADMIN_CREDS_FILE}: {e}")
        print("                 Authentication will be disabled.")

def save_admin_credentials(email: str, api_key_hash: str):
    """Save admin credentials to the file."""
    ADMIN_CREDS_FILE.parent.mkdir(parents=True, exist_ok=True) # Ensure directory exists
    creds = {
        "email": email,
        "api_key_hash": api_key_hash
    }
    try:
        with open(ADMIN_CREDS_FILE, 'w') as f:
            json.dump(creds, f, indent=4)
        os.chmod(ADMIN_CREDS_FILE, 0o600) # Set restrictive permissions
        print(f"Admin credentials saved to {ADMIN_CREDS_FILE}")
    except IOError as e:
        print(f"!!! ERROR !!! Failed to save admin credentials to {ADMIN_CREDS_FILE}: {e}")
        raise # Re-raise to potentially stop the application

async def first_time_setup():
    """
    First-time setup for the admin user.
    """
    print("--- FIRST TIME ADMIN SETUP ---")
    if ADMIN_CREDS_FILE.exists():
        print("Admin credentials already exist. Skipping setup.")
        return
    
    print("No existing admin credentials found.")
    print("Creating initial admin user...")
    
    # In a real scenario, you'd prompt for email and password here.
    # For simplicity, we'll use placeholders.
    admin_email = "admin@db-forge.local" 
    admin_password = "admin"  # Default password, should be changed by user
    
    # Hash the password
    password_hash = pwd_context.hash(admin_password)
    
    # Save the credentials
    ADMIN_CREDS_FILE.parent.mkdir(parents=True, exist_ok=True) # Ensure directory exists
    creds = {
        "email": admin_email,
        "password_hash": password_hash
    }
    try:
        with open(ADMIN_CREDS_FILE, 'w') as f:
            json.dump(creds, f, indent=4)
        os.chmod(ADMIN_CREDS_FILE, 0o600) # Set restrictive permissions
        print(f"Admin credentials saved to {ADMIN_CREDS_FILE}")
    except IOError as e:
        print(f"!!! ERROR !!! Failed to save admin credentials to {ADMIN_CREDS_FILE}: {e}")
        raise # Re-raise to potentially stop the application
    
    print(f"--- INITIAL ADMIN USER CREATED ---")
    print(f"Email: {admin_email}")
    print(f"Password: {admin_password} (CHANGE THIS IMMEDIATELY)")
    print("--- SETUP COMPLETE ---")

async def verify_admin_credentials(email: str, password: str) -> bool:
    """
    Verify admin credentials.
    """
    if not ADMIN_CREDS_FILE.exists():
        return False
    
    try:
        with open(ADMIN_CREDS_FILE, 'r') as f:
            data = json.load(f)
        
        if "email" not in data or "password_hash" not in data:
            return False
            
        if data["email"] != email:
            return False
            
        return pwd_context.verify(password, data["password_hash"])
    except (json.JSONDecodeError, KeyError, IOError) as e:
        print(f"!!! ERROR !!! Failed to verify admin credentials: {e}")
        return False

async def verify_api_key_header(api_key_header: str = Depends(api_key_header)):
    """
    FastAPI dependency to verify the API key from the header.
    
    Args:
        api_key_header (str, optional): The API key provided in the header.
        
    Raises:
        HTTPException: 
            - 401 Unauthorized: If the key is missing or invalid.
            - 503 Service Unavailable: If auth is misconfigured.
    """
    # Check if auth is configured
    if not ADMIN_API_KEY_HASH:
        # This could mean auth is disabled or misconfigured
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not properly configured on the server."
        )

    # Check if key was provided
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key. Please provide a valid API key in the X-API-Key header.",
            headers={"WWW-Authenticate": f"ApiKeyHeader"}, # Standard header name
        )
    
    # Verify the key
    if not verify_api_key(api_key_header, ADMIN_API_KEY_HASH):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key.",
            headers={"WWW-Authenticate": f"ApiKeyHeader"},
        )
        
    # If we get here, the key is valid
    return True # or return the API key itself if needed by the endpoint