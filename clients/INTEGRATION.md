# DB-Forge Client Integration Guide

This document provides practical examples of integrating DB-Forge clients into your applications.

## Quick Integration Examples

### Web Application Backend

**Python (FastAPI/Flask):**
```python
from fastapi import FastAPI, HTTPException
from dbforge_client import DBForgeClient, DatabaseNotFound

app = FastAPI()
dbforge = DBForgeClient()

@app.on_event("startup")
async def startup():
    # Initialize application database
    dbforge.spawn_database("app_main")
    db = dbforge.get_database("app_main")
    
    # Setup schema
    db.create_table("users", [
        {"name": "id", "type": "INTEGER", "primary_key": True},
        {"name": "email", "type": "TEXT", "not_null": True, "unique": True},
        {"name": "created_at", "type": "DATETIME", "default": "CURRENT_TIMESTAMP"}
    ])

@app.post("/users")
async def create_user(email: str):
    try:
        db = dbforge.get_database("app_main")
        result = db.insert_rows("users", [{"email": email}])
        return {"success": True, "rows_affected": result["rows_affected"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users")
async def get_users():
    db = dbforge.get_database("app_main")
    return db.select_rows("users")
```

**C++ (REST Service):**
```cpp
#include <dbforge/dbforge.hpp>
#include <microhttpd.h>  // Example web server

class UserService {
private:
    dbforge::Client client;
    
public:
    UserService() : client("http://db.localhost") {
        // Initialize service database
        client.spawn_database("user_service");
        auto db = client.get_database("user_service");
        
        db.create_table("users", {
            {"id", "INTEGER", true, false},
            {"email", "TEXT", false, true},
            {"created_at", "DATETIME", false, false, "CURRENT_TIMESTAMP"}
        });
    }
    
    std::string create_user(const std::string& email) {
        try {
            auto db = client.get_database("user_service");
            auto result = db.insert_rows("users", {{{"email", email}}});
            return "{\"success\": true, \"rows_affected\": " + 
                   std::to_string(result.rows_affected) + "}";
        } catch (const dbforge::Exception& e) {
            return "{\"error\": \"" + std::string(e.what()) + "\"}";
        }
    }
};
```

### Microservices Architecture

**Service Per Database Pattern:**
```python
# user_service.py
class UserService:
    def __init__(self):
        self.client = DBForgeClient()
        self.client.spawn_database("users_db")
        self.db = self.client.get_database("users_db")
        self._setup_schema()
    
    def _setup_schema(self):
        self.db.create_table("users", [
            {"name": "id", "type": "INTEGER", "primary_key": True},
            {"name": "username", "type": "TEXT", "not_null": True},
            {"name": "email", "type": "TEXT", "not_null": True}
        ])

# order_service.py  
class OrderService:
    def __init__(self):
        self.client = DBForgeClient()
        self.client.spawn_database("orders_db")
        self.db = self.client.get_database("orders_db")
        self._setup_schema()
    
    def _setup_schema(self):
        self.db.create_table("orders", [
            {"name": "id", "type": "INTEGER", "primary_key": True},
            {"name": "user_id", "type": "INTEGER", "not_null": True},
            {"name": "total", "type": "REAL", "not_null": True}
        ])
```

### Data Analytics Pipeline

**Python (Pandas Integration):**
```python
import pandas as pd
from dbforge_client import DBForgeClient

class DataAnalytics:
    def __init__(self):
        self.client = DBForgeClient()
        
    def analyze_user_behavior(self, days=30):
        # Get data from multiple databases
        users_db = self.client.get_database("users_db")
        events_db = self.client.get_database("events_db")
        
        # Extract data
        users = users_db.select_rows("users")
        events = events_db.execute_query(
            "SELECT * FROM events WHERE created_at > datetime('now', '-{} days')".format(days)
        )
        
        # Convert to pandas DataFrames
        users_df = pd.DataFrame(users)
        events_df = pd.DataFrame(events['data'])
        
        # Perform analysis
        user_activity = events_df.groupby('user_id').size().reset_index(name='event_count')
        
        return users_df.merge(user_activity, on='user_id', how='left')
    
    def store_results(self, df, table_name):
        # Create analytics database if needed
        self.client.spawn_database("analytics_db")
        analytics_db = self.client.get_database("analytics_db")
        
        # Convert DataFrame to DB-Forge format
        rows = df.to_dict('records')
        analytics_db.insert_rows(table_name, rows)
```

### Multi-tenant Application

**Database-per-tenant:**
```python
class TenantManager:
    def __init__(self):
        self.client = DBForgeClient()
    
    def create_tenant(self, tenant_id):
        db_name = f"tenant_{tenant_id}"
        self.client.spawn_database(db_name)
        
        # Setup tenant schema
        db = self.client.get_database(db_name)
        db.create_table("users", [
            {"name": "id", "type": "INTEGER", "primary_key": True},
            {"name": "username", "type": "TEXT", "not_null": True}
        ])
        
        return db_name
    
    def get_tenant_db(self, tenant_id):
        return self.client.get_database(f"tenant_{tenant_id}")
    
    def delete_tenant(self, tenant_id):
        self.client.prune_database(f"tenant_{tenant_id}")
```

### Testing with DB-Forge

**Pytest Integration:**
```python
import pytest
from dbforge_client import DBForgeClient

@pytest.fixture
def test_db():
    client = DBForgeClient()
    db_name = "test_db_" + str(uuid.uuid4())
    
    # Setup
    client.spawn_database(db_name)
    db = client.get_database(db_name)
    
    yield db
    
    # Cleanup
    client.prune_database(db_name)

def test_user_creation(test_db):
    test_db.create_table("users", [
        {"name": "id", "type": "INTEGER", "primary_key": True},
        {"name": "email", "type": "TEXT", "not_null": True}
    ])
    
    result = test_db.insert_rows("users", [{"email": "test@example.com"}])
    assert result["rows_affected"] == 1
    
    users = test_db.select_rows("users")
    assert len(users) == 1
    assert users[0]["email"] == "test@example.com"
```

### Docker Integration

**Docker Compose with DB-Forge:**
```yaml
version: '3.8'
services:
  db-forge:
    build: ./db-forge
    ports:
      - "8080:8080"
    volumes:
      - ./db-data:/data
  
  app:
    build: ./app
    environment:
      - DBFORGE_BASE_URL=http://db-forge:8080
    depends_on:
      - db-forge
```

**Application Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install DB-Forge client
RUN pip install dbforge-client

COPY . .
CMD ["python", "app.py"]
```

### Configuration Management

**Environment-based Configuration:**
```python
import os
from dbforge_client import DBForgeClient

class Config:
    DBFORGE_BASE_URL = os.getenv('DBFORGE_BASE_URL', 'http://localhost:8080')
    DBFORGE_API_KEY = os.getenv('DBFORGE_API_KEY')
    DBFORGE_TIMEOUT = int(os.getenv('DBFORGE_TIMEOUT', '30'))

class Application:
    def __init__(self):
        self.dbforge = DBForgeClient(
            base_url=Config.DBFORGE_BASE_URL,
            api_key=Config.DBFORGE_API_KEY,
            timeout=Config.DBFORGE_TIMEOUT
        )
```

### Error Handling Patterns

**Resilient Service Pattern:**
```python
import time
import logging
from dbforge_client import DBForgeClient, ConnectionError, TimeoutError

class ResilientDBForgeService:
    def __init__(self, max_retries=3, backoff_factor=2):
        self.client = DBForgeClient()
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.logger = logging.getLogger(__name__)
    
    def execute_with_retry(self, operation, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except (ConnectionError, TimeoutError) as e:
                if attempt == self.max_retries - 1:
                    self.logger.error(f"Failed after {self.max_retries} attempts: {e}")
                    raise
                
                wait_time = self.backoff_factor ** attempt
                self.logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
    
    def safe_query(self, db_name, sql, params=None):
        def _query():
            db = self.client.get_database(db_name)
            return db.execute_query(sql, params or [])
        
        return self.execute_with_retry(_query)
```

### Performance Optimization

**Connection Pooling Pattern (Python Async):**
```python
import asyncio
from dbforge_client import AsyncDBForgeClient

class DBForgePool:
    def __init__(self, pool_size=10):
        self.pool_size = pool_size
        self.clients = []
        self.available = asyncio.Queue(maxsize=pool_size)
    
    async def initialize(self):
        for _ in range(self.pool_size):
            client = AsyncDBForgeClient()
            self.clients.append(client)
            await self.available.put(client)
    
    async def get_client(self):
        return await self.available.get()
    
    async def return_client(self, client):
        await self.available.put(client)
    
    async def close(self):
        for client in self.clients:
            await client.close()

# Usage
pool = DBForgePool()
await pool.initialize()

client = await pool.get_client()
try:
    # Use client
    db = client.get_database("my_db")
    result = await db.execute_query("SELECT * FROM users")
finally:
    await pool.return_client(client)
```

### Monitoring and Logging

**Structured Logging:**
```python
import logging
import json
from dbforge_client import DBForgeClient

class LoggingDBForgeClient:
    def __init__(self):
        self.client = DBForgeClient()
        self.logger = logging.getLogger(__name__)
    
    def execute_query(self, db_name, sql, params=None):
        start_time = time.time()
        
        try:
            db = self.client.get_database(db_name)
            result = db.execute_query(sql, params)
            
            duration = time.time() - start_time
            self.logger.info(json.dumps({
                'event': 'query_success',
                'database': db_name,
                'sql': sql,
                'duration_ms': int(duration * 1000),
                'rows_affected': result.get('rows_affected', 0)
            }))
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(json.dumps({
                'event': 'query_error',
                'database': db_name,
                'sql': sql,
                'duration_ms': int(duration * 1000),
                'error': str(e)
            }))
            raise
```

## Best Practices

### 1. Database Lifecycle Management
- **Create databases on application startup**
- **Use meaningful database names** (e.g., `app_users`, `service_orders`)
- **Clean up test databases** in CI/CD pipelines
- **Monitor database count** to prevent resource exhaustion

### 2. Schema Management
- **Version your schemas** using migration scripts
- **Use consistent column naming** conventions
- **Add indexes** for frequently queried columns
- **Document schema changes** in version control

### 3. Error Handling
- **Always wrap DB calls** in try-catch blocks
- **Implement retry logic** for transient failures
- **Log errors with context** (database name, SQL, parameters)
- **Fail fast** for permanent errors (auth, bad SQL)

### 4. Performance
- **Use batch operations** when inserting multiple rows
- **Limit result set sizes** with LIMIT clauses
- **Use parameterized queries** to prevent SQL injection
- **Consider connection pooling** for high-concurrency applications

### 5. Testing
- **Use isolated databases** for each test
- **Clean up resources** after tests complete
- **Test error conditions** not just happy paths
- **Use fixtures** for common test data

### 6. Security
- **Use API keys** in production environments
- **Validate input parameters** before querying
- **Use parameterized queries** to prevent SQL injection
- **Limit database access** to authorized services only

This integration guide should help you get started with DB-Forge in your specific use case. For more examples, check the `examples/` directories in each client library.