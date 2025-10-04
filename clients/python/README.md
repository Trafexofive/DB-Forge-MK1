# DB-Forge Python Client

A Python client library for Praetorian DB-Forge that makes it easy to interact with your DB-Forge instances.

## Installation

```bash
pip install dbforge-client
```

Or for development:

```bash
pip install -e .
```

## Quick Start

```python
from dbforge_client import DBForgeClient

# Initialize client
client = DBForgeClient(
    base_url="http://db.localhost",
    api_key="your-api-key"  # Optional
)

# Admin operations
client.spawn_database("my-app-db")
databases = client.list_databases()
print(f"Active databases: {databases}")

# Database operations
db = client.get_database("my-app-db")

# Create a table
db.create_table("users", [
    {"name": "id", "type": "INTEGER", "primary_key": True},
    {"name": "username", "type": "TEXT", "not_null": True},
    {"name": "email", "type": "TEXT", "not_null": True},
    {"name": "created_at", "type": "DATETIME", "default": "CURRENT_TIMESTAMP"}
])

# Insert data
db.insert_rows("users", [
    {"username": "alice", "email": "alice@example.com"},
    {"username": "bob", "email": "bob@example.com"}
])

# Query data
users = db.select_rows("users", {"username": "alice"})
print(f"Found users: {users}")

# Raw SQL queries
result = db.execute_query(
    "SELECT COUNT(*) as user_count FROM users WHERE created_at > ?",
    ["2023-01-01"]
)
print(f"User count: {result}")

# Cleanup
client.prune_database("my-app-db")
```

## Features

- **Simple API**: Easy-to-use Python interface for all DB-Forge operations
- **Type Safety**: Full type hints for better IDE support and error catching
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Async Support**: Both synchronous and asynchronous clients available
- **CLI Tool**: Command-line interface for quick operations
- **Connection Pooling**: Efficient HTTP connection management
- **Retry Logic**: Built-in retry mechanisms for reliability

## API Reference

### DBForgeClient

Main client class for interacting with DB-Forge.

#### Methods

##### Admin Operations
- `spawn_database(name: str) -> Dict[str, Any]`
- `prune_database(name: str) -> Dict[str, Any]`
- `list_databases() -> List[Dict[str, Any]]`

##### Database Operations
- `get_database(name: str) -> DBForgeDatabase`

### DBForgeDatabase

Database-specific operations.

#### Methods

##### Table Operations
- `create_table(name: str, columns: List[Dict[str, Any]]) -> Dict[str, Any]`
- `insert_rows(table: str, rows: List[Dict[str, Any]]) -> Dict[str, Any]`
- `select_rows(table: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]`

##### Query Operations
- `execute_query(sql: str, params: List[Any] = None) -> Dict[str, Any]`

## CLI Usage

The package includes a command-line tool:

```bash
# Set API key (optional)
export DBFORGE_API_KEY="your-key"

# Admin operations
dbforge spawn my-db
dbforge list
dbforge prune my-db

# Query operations
dbforge query my-db "SELECT * FROM users"
dbforge query my-db "INSERT INTO users (username, email) VALUES (?, ?)" alice alice@example.com
```

## Configuration

### Environment Variables

- `DBFORGE_BASE_URL`: Default base URL (default: http://db.localhost)
- `DBFORGE_API_KEY`: Default API key
- `DBFORGE_TIMEOUT`: Request timeout in seconds (default: 30)

### Client Configuration

```python
client = DBForgeClient(
    base_url="http://db.localhost",
    api_key="your-api-key",
    timeout=30,
    retries=3,
    backoff_factor=0.3
)
```

## Error Handling

```python
from dbforge_client import DBForgeClient, DBForgeError, DatabaseNotFound

client = DBForgeClient()

try:
    client.spawn_database("my-db")
    db = client.get_database("my-db")
    result = db.execute_query("SELECT * FROM non_existent_table")
except DatabaseNotFound as e:
    print(f"Database not found: {e}")
except DBForgeError as e:
    print(f"DB-Forge error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Async Usage

```python
import asyncio
from dbforge_client import AsyncDBForgeClient

async def main():
    client = AsyncDBForgeClient()
    
    await client.spawn_database("async-db")
    db = await client.get_database("async-db")
    
    result = await db.execute_query("SELECT 1 as test")
    print(result)
    
    await client.prune_database("async-db")

asyncio.run(main())
```

## Contributing

1. Clone the repository
2. Install development dependencies: `pip install -e .[dev]`
3. Run tests: `pytest`
4. Format code: `black . && isort .`
5. Type check: `mypy dbforge_client`

## License

MIT License - see LICENSE file for details.