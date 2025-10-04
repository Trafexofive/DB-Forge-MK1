# 🔌 DB-Forge MK1 API Specification

This document provides comprehensive documentation for the DB-Forge MK1 RESTful API, including authentication, error handling, and all available endpoints.

**Base URL**: `http://db.localhost:8081` (via Traefik proxy)  
**Direct URL**: `http://localhost:8000` (development only)  
**API Version**: v1  
**Documentation**: http://db.localhost:8081/docs (Interactive Swagger UI)

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Error Handling](#error-handling)  
3. [Admin API - Database Management](#admin-api)
4. [Data API - Database Operations](#data-api)
5. [Monitoring API - Health & Status](#monitoring-api)
6. [Client Examples](#client-examples)

---

## 🔐 Authentication

### Current State
The current MK1 release operates without authentication for simplicity during development. All endpoints are publicly accessible.

### Planned (MK2)
Future releases will include:
- **JWT Authentication**: Bearer token authentication
- **API Keys**: Long-lived tokens for service-to-service communication  
- **Role-Based Access**: Admin, user, and read-only roles
- **Rate Limiting**: Request throttling per client/IP

---

## 🚨 Error Handling

All API responses follow a consistent error format with appropriate HTTP status codes.

### Error Response Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error description",
    "status": 400,
    "details": {
      "field": "Additional context when applicable"
    }
  }
}
```

### Common HTTP Status Codes
- **200 OK**: Successful request
- **201 Created**: Resource successfully created
- **400 Bad Request**: Invalid request data or parameters
- **404 Not Found**: Requested resource does not exist
- **409 Conflict**: Resource already exists
- **422 Unprocessable Entity**: Valid JSON but business logic error
- **500 Internal Server Error**: Unexpected server error

### Error Code Examples
```json
{
  "error": {
    "code": "DATABASE_NOT_FOUND",
    "message": "Database 'user-app' does not exist",
    "status": 404
  }
}
```

```json
{
  "error": {
    "code": "INVALID_SQL_QUERY", 
    "message": "SQL syntax error near 'SELCT'",
    "status": 400,
    "details": {
      "query": "SELCT * FROM users",
      "position": 1
    }
  }
}
```

---

## 🛠️ Admin API - Database Management

The Admin API handles database lifecycle operations including creation, deletion, and listing of database instances.

### Create Database Instance

**Endpoint**: `POST /admin/databases/spawn/{db_name}`  
**Description**: Creates a new isolated SQLite database instance with its own container.

#### Parameters
- **db_name** (path, required): Database identifier (alphanumeric, hyphens, underscores only)

#### Request Body
None required. Optional configuration in future versions.

#### Success Response (201 Created)
```json
{
  "message": "Database instance spawned successfully",
  "database": {
    "name": "user-analytics",
    "status": "running",
    "container_id": "a1b2c3d4e5f6",
    "created_at": "2024-01-15T10:30:00Z",
    "file_path": "/databases/user-analytics.db",
    "size_bytes": 8192
  }
}
```

#### Error Responses
```json
// Database name invalid
{
  "error": {
    "code": "INVALID_DATABASE_NAME",
    "message": "Database name must contain only letters, numbers, hyphens and underscores",
    "status": 400
  }
}

// Database already exists  
{
  "error": {
    "code": "DATABASE_ALREADY_EXISTS",
    "message": "Database 'user-analytics' already exists",
    "status": 409
  }
}
```

#### cURL Example
```bash
curl -X POST http://db.localhost:8081/admin/databases/spawn/user-analytics \
  -H "Content-Type: application/json"
```

---

### List Database Instances

**Endpoint**: `GET /admin/databases`  
**Description**: Retrieves a list of all database instances and their status.

#### Query Parameters
- **status** (optional): Filter by status (`running`, `stopped`, `error`)
- **limit** (optional): Maximum number of results (default: 100)
- **offset** (optional): Pagination offset (default: 0)

#### Success Response (200 OK)
```json
{
  "databases": [
    {
      "name": "user-analytics",
      "status": "running", 
      "container_id": "a1b2c3d4e5f6",
      "created_at": "2024-01-15T10:30:00Z",
      "last_accessed": "2024-01-15T14:22:30Z",
      "file_path": "/databases/user-analytics.db",
      "size_bytes": 1048576,
      "connection_count": 3
    },
    {
      "name": "session-store",
      "status": "running",
      "container_id": "b2c3d4e5f6g7", 
      "created_at": "2024-01-14T09:15:00Z",
      "last_accessed": "2024-01-15T14:20:15Z",
      "file_path": "/databases/session-store.db",
      "size_bytes": 524288,
      "connection_count": 1
    }
  ],
  "total": 2,
  "limit": 100,
  "offset": 0
}
```

#### cURL Example
```bash
# List all databases
curl http://db.localhost:8081/admin/databases

# List only running databases with pagination
curl "http://db.localhost:8081/admin/databases?status=running&limit=50&offset=0"
```

---

### Get Database Details

**Endpoint**: `GET /admin/databases/{db_name}`  
**Description**: Retrieves detailed information about a specific database instance.

#### Success Response (200 OK)
```json
{
  "database": {
    "name": "user-analytics", 
    "status": "running",
    "container_id": "a1b2c3d4e5f6",
    "created_at": "2024-01-15T10:30:00Z",
    "last_accessed": "2024-01-15T14:22:30Z",
    "file_path": "/databases/user-analytics.db",
    "size_bytes": 1048576,
    "connection_count": 3,
    "tables": [
      {
        "name": "users",
        "row_count": 1250,
        "size_bytes": 524288
      },
      {
        "name": "events", 
        "row_count": 45000,
        "size_bytes": 524288
      }
    ],
    "indexes": ["idx_users_email", "idx_events_timestamp"],
    "schema_version": "1.0"
  }
}
```

---

### Delete Database Instance

**Endpoint**: `DELETE /admin/databases/{db_name}`  
**Description**: Permanently deletes a database instance, its container, and data file.

#### Query Parameters
- **force** (optional): Skip confirmation for automated scripts (`true`/`false`)

#### Success Response (200 OK)
```json
{
  "message": "Database 'user-analytics' deleted successfully",
  "deleted_at": "2024-01-15T15:45:00Z",
  "container_removed": true,
  "file_removed": true
}
```

#### Error Response
```json
{
  "error": {
    "code": "DATABASE_NOT_FOUND",
    "message": "Database 'nonexistent-db' does not exist", 
    "status": 404
  }
}
```

#### cURL Example
```bash
curl -X DELETE http://db.localhost:8081/admin/databases/user-analytics
```

---

## 📊 Data API - Database Operations

The Data API provides endpoints for executing SQL queries, managing schemas, and performing CRUD operations on database contents.

### Execute SQL Query

**Endpoint**: `POST /api/db/{db_name}/query`  
**Description**: Executes arbitrary SQL queries against the specified database.

#### Request Body
```json
{
  "sql": "SELECT * FROM users WHERE age > ? AND status = ?",
  "parameters": [25, "active"],
  "limit": 100,
  "format": "json"
}
```

#### Parameters
- **sql** (required): SQL query string
- **parameters** (optional): Array of parameter values for prepared statements
- **limit** (optional): Maximum number of rows to return (default: 1000)
- **format** (optional): Response format (`json`, `csv`) - default: `json`

#### Success Response - SELECT Query (200 OK)
```json
{
  "query": "SELECT * FROM users WHERE age > ? AND status = ?",
  "parameters": [25, "active"],
  "results": [
    {
      "id": 1,
      "name": "John Doe", 
      "email": "john@example.com",
      "age": 30,
      "status": "active",
      "created_at": "2024-01-10T12:00:00Z"
    },
    {
      "id": 2,
      "name": "Jane Smith",
      "email": "jane@example.com", 
      "age": 28,
      "status": "active",
      "created_at": "2024-01-12T09:30:00Z"
    }
  ],
  "row_count": 2,
  "execution_time_ms": 15,
  "has_more": false
}
```

#### Success Response - INSERT/UPDATE/DELETE (200 OK)
```json
{
  "query": "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
  "parameters": ["Alice Johnson", "alice@example.com", 32],
  "affected_rows": 1,
  "last_insert_id": 3,
  "execution_time_ms": 8
}
```

#### Error Responses
```json
// SQL Syntax Error
{
  "error": {
    "code": "SQL_SYNTAX_ERROR",
    "message": "SQL syntax error: no such column: invalid_column",
    "status": 400,
    "details": {
      "query": "SELECT invalid_column FROM users",
      "position": 7
    }
  }
}

// Database locked
{
  "error": {
    "code": "DATABASE_LOCKED", 
    "message": "Database is locked by another process",
    "status": 423,
    "details": {
      "retry_after_ms": 1000
    }
  }
}
```

#### cURL Examples
```bash
# Simple SELECT query
curl -X POST http://db.localhost:8081/api/db/user-analytics/query \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM users LIMIT 10"}'

# Parameterized query  
curl -X POST http://db.localhost:8081/api/db/user-analytics/query \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT * FROM users WHERE age > ? AND status = ?",
    "parameters": [25, "active"],
    "limit": 50
  }'

# INSERT operation
curl -X POST http://db.localhost:8081/api/db/user-analytics/query \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
    "parameters": ["Bob Wilson", "bob@example.com", 35]
  }'
```

---

### Create Table (Convenience Endpoint)

**Endpoint**: `POST /api/db/{db_name}/tables`  
**Description**: Creates a new table with specified schema (convenience wrapper around CREATE TABLE).

#### Request Body
```json
{
  "table_name": "products",
  "columns": [
    {
      "name": "id",
      "type": "INTEGER",
      "constraints": ["PRIMARY KEY", "AUTOINCREMENT"]
    },
    {
      "name": "name", 
      "type": "TEXT",
      "constraints": ["NOT NULL"]
    },
    {
      "name": "price",
      "type": "DECIMAL(10,2)",
      "constraints": ["NOT NULL", "CHECK(price > 0)"]
    },
    {
      "name": "created_at",
      "type": "DATETIME",
      "constraints": ["DEFAULT CURRENT_TIMESTAMP"]
    }
  ],
  "indexes": [
    {
      "name": "idx_products_name",
      "columns": ["name"],
      "unique": true
    }
  ]
}
```

#### Success Response (201 Created)
```json
{
  "message": "Table 'products' created successfully",
  "table_name": "products", 
  "columns": 4,
  "indexes": 1,
  "sql": "CREATE TABLE products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, price DECIMAL(10,2) NOT NULL CHECK(price > 0), created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
}
```

---

### Insert Data (Convenience Endpoint)

**Endpoint**: `POST /api/db/{db_name}/tables/{table_name}/rows`  
**Description**: Inserts one or more rows into the specified table.

#### Request Body
```json
{
  "rows": [
    {
      "name": "Laptop Pro",
      "price": 1299.99
    },
    {
      "name": "Wireless Mouse", 
      "price": 29.99
    }
  ]
}
```

#### Success Response (201 Created)
```json
{
  "message": "2 rows inserted successfully",
  "table_name": "products",
  "inserted_rows": 2,
  "last_insert_ids": [1, 2]
}
```

---

### Get Table Data

**Endpoint**: `GET /api/db/{db_name}/tables/{table_name}/rows`  
**Description**: Retrieves rows from the specified table with optional filtering and pagination.

#### Query Parameters
- **limit** (optional): Maximum rows to return (default: 100, max: 1000)
- **offset** (optional): Number of rows to skip for pagination (default: 0)  
- **order_by** (optional): Column to sort by (default: primary key)
- **order** (optional): Sort direction (`asc` or `desc`, default: `asc`)
- **where** (optional): WHERE clause conditions (URL encoded)

#### Success Response (200 OK)
```json
{
  "table_name": "products",
  "rows": [
    {
      "id": 1,
      "name": "Laptop Pro", 
      "price": 1299.99,
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "name": "Wireless Mouse",
      "price": 29.99, 
      "created_at": "2024-01-15T10:31:00Z"
    }
  ],
  "total_rows": 2,
  "limit": 100,
  "offset": 0,
  "has_more": false
}
```

#### cURL Example
```bash
# Get all rows
curl http://db.localhost:8081/api/db/user-analytics/tables/products/rows

# Get rows with pagination and filtering
curl "http://db.localhost:8081/api/db/user-analytics/tables/products/rows?limit=50&offset=0&order_by=price&order=desc&where=price%20%3E%20100"
```

---

### Get Database Schema

**Endpoint**: `GET /api/db/{db_name}/schema`  
**Description**: Returns the complete schema information for the database.

#### Query Parameters
- **table** (optional): Get schema for specific table only

#### Success Response (200 OK)
```json
{
  "database": "user-analytics",
  "tables": [
    {
      "name": "users",
      "columns": [
        {
          "name": "id",
          "type": "INTEGER",
          "nullable": false,
          "primary_key": true,
          "auto_increment": true
        },
        {
          "name": "email", 
          "type": "TEXT",
          "nullable": false,
          "unique": true
        },
        {
          "name": "created_at",
          "type": "DATETIME",
          "nullable": false,
          "default": "CURRENT_TIMESTAMP"
        }
      ],
      "indexes": [
        {
          "name": "idx_users_email",
          "columns": ["email"],
          "unique": true
        }
      ],
      "row_count": 1250
    }
  ]
}
```

---

## 💚 Monitoring API - Health & Status

### Health Check

**Endpoint**: `GET /health`  
**Description**: Returns the overall health status of the DB Gateway service.

#### Success Response (200 OK)
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T14:30:00Z",
  "version": "1.0.0",
  "uptime_seconds": 86400,
  "checks": {
    "database_connectivity": "ok",
    "docker_daemon": "ok", 
    "filesystem": "ok",
    "memory_usage": "ok"
  }
}
```

#### Unhealthy Response (503 Service Unavailable)
```json
{
  "status": "unhealthy",
  "timestamp": "2024-01-15T14:30:00Z",
  "version": "1.0.0", 
  "uptime_seconds": 86400,
  "checks": {
    "database_connectivity": "ok",
    "docker_daemon": "error",
    "filesystem": "ok", 
    "memory_usage": "warning"
  },
  "errors": [
    "Docker daemon is not responding",
    "Memory usage above 90% threshold"
  ]
}
```

---

### System Statistics

**Endpoint**: `GET /admin/stats`  
**Description**: Returns detailed system statistics and metrics.

#### Success Response (200 OK)
```json
{
  "system": {
    "timestamp": "2024-01-15T14:30:00Z",
    "uptime_seconds": 86400,
    "memory_usage": {
      "used_bytes": 134217728,
      "available_bytes": 1073741824,
      "usage_percent": 12.5
    },
    "cpu_usage_percent": 8.2,
    "disk_usage": {
      "data_path": "./db-data",
      "used_bytes": 2147483648,
      "available_bytes": 10737418240,
      "usage_percent": 20.0
    }
  },
  "databases": {
    "total_count": 12,
    "running_count": 10,
    "stopped_count": 2,
    "total_size_bytes": 2147483648,
    "average_size_bytes": 178956970
  },
  "api_metrics": {
    "total_requests": 15420,
    "requests_per_second": 2.5,
    "average_response_time_ms": 45,
    "error_rate_percent": 0.2
  }
}
```

---

## 📖 Client Examples

### Python Client Example
```python
import requests
import json

class DBForgeClient:
    def __init__(self, base_url="http://db.localhost:8081"):
        self.base_url = base_url
    
    def create_database(self, name):
        response = requests.post(f"{self.base_url}/admin/databases/spawn/{name}")
        return response.json()
    
    def execute_query(self, db_name, sql, parameters=None):
        data = {"sql": sql}
        if parameters:
            data["parameters"] = parameters
        
        response = requests.post(
            f"{self.base_url}/api/db/{db_name}/query",
            json=data
        )
        return response.json()
    
    def list_databases(self):
        response = requests.get(f"{self.base_url}/admin/databases")
        return response.json()

# Usage example
client = DBForgeClient()

# Create database
result = client.create_database("my-app")
print(f"Created database: {result}")

# Execute query  
result = client.execute_query(
    "my-app", 
    "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)"
)
print(f"Table created: {result}")

# Insert data
result = client.execute_query(
    "my-app",
    "INSERT INTO users (name, email) VALUES (?, ?)",
    ["John Doe", "john@example.com"]
)
print(f"Data inserted: {result}")

# Query data
result = client.execute_query(
    "my-app",
    "SELECT * FROM users WHERE name LIKE ?", 
    ["%John%"]
)
print(f"Query results: {result}")
```

### JavaScript/Node.js Example
```javascript
class DBForgeClient {
    constructor(baseUrl = 'http://db.localhost:8081') {
        this.baseUrl = baseUrl;
    }
    
    async createDatabase(name) {
        const response = await fetch(`${this.baseUrl}/admin/databases/spawn/${name}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        return response.json();
    }
    
    async executeQuery(dbName, sql, parameters = null) {
        const data = { sql };
        if (parameters) data.parameters = parameters;
        
        const response = await fetch(`${this.baseUrl}/api/db/${dbName}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    }
    
    async listDatabases() {
        const response = await fetch(`${this.baseUrl}/admin/databases`);
        return response.json();
    }
}

// Usage example
const client = new DBForgeClient();

(async () => {
    // Create database
    const createResult = await client.createDatabase('my-app');
    console.log('Created database:', createResult);
    
    // Create table
    const tableResult = await client.executeQuery(
        'my-app',
        'CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL)'
    );
    console.log('Table created:', tableResult);
    
    // Insert data
    const insertResult = await client.executeQuery(
        'my-app', 
        'INSERT INTO products (name, price) VALUES (?, ?)',
        ['Laptop', 999.99]
    );
    console.log('Data inserted:', insertResult);
    
    // Query data
    const queryResult = await client.executeQuery(
        'my-app',
        'SELECT * FROM products WHERE price > ?',
        [500]
    );
    console.log('Query results:', queryResult);
})();
```

### cURL Script Example
```bash
#!/bin/bash

BASE_URL="http://db.localhost:8081"
DB_NAME="example-db"

echo "Creating database..."
curl -X POST "$BASE_URL/admin/databases/spawn/$DB_NAME" \
    -H "Content-Type: application/json"

echo -e "\n\nCreating table..."
curl -X POST "$BASE_URL/api/db/$DB_NAME/query" \
    -H "Content-Type: application/json" \
    -d '{
        "sql": "CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL, completed BOOLEAN DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
    }'

echo -e "\n\nInserting sample data..."
curl -X POST "$BASE_URL/api/db/$DB_NAME/query" \
    -H "Content-Type: application/json" \
    -d '{
        "sql": "INSERT INTO tasks (title, completed) VALUES (?, ?), (?, ?), (?, ?)",
        "parameters": ["Learn DB-Forge API", false, "Build awesome app", false, "Deploy to production", false]
    }'

echo -e "\n\nQuerying all tasks..."
curl -X POST "$BASE_URL/api/db/$DB_NAME/query" \
    -H "Content-Type: application/json" \
    -d '{"sql": "SELECT * FROM tasks ORDER BY created_at DESC"}'

echo -e "\n\nGetting database list..."
curl "$BASE_URL/admin/databases"
```

---

## 📚 Additional Resources

- **Interactive API Documentation**: http://db.localhost:8081/docs (Swagger UI)
- **OpenAPI Spec**: http://db.localhost:8081/openapi.json
- **Client Libraries**: See `/clients` directory for official SDKs
- **Architecture Documentation**: [docs/ARCHITECTURE.md](ARCHITECTURE.md)
- **Contributing Guide**: [docs/CONTRIBUTING.md](CONTRIBUTING.md)

---

**Need help?** Check out the [GitHub Issues](https://github.com/your-org/db-forge/issues) or [Discussions](https://github.com/your-org/db-forge/discussions) for community support.
    }
    ```

### `POST /admin/databases/prune/{db_name}`

Stops and removes a specific database instance container. **Note: This does not delete the data volume.**

-   **URL Params:**
    -   `db_name` (string, required): The name of the database to prune.
-   **Success Response (200 OK):**
    ```json
    {
      "message": "Database instance pruned successfully.",
      "db_name": "agent-alpha-memory"
    }
    ```
-   **Error Response (404 Not Found):** If no database instance with that name is found.
    ```json
    {
      "error": {
        "code": "NOT_FOUND",
        "message": "Database instance not found.",
        "status": 404
      }
    }
    ```

### `GET /admin/databases`

Lists all currently managed database instances.

-   **Success Response (200 OK):**
    ```json
    [
      {
        "name": "agent-alpha-memory",
        "container_id": "a1b2c3d4e5f6...",
        "status": "running"
      }
    ]
    ```

---

## 2. Data Plane API

These endpoints are for interacting with the data inside a specific database.



### `POST /api/db/{db_name}/query`

Executes a raw SQL query against the specified database. This is the most flexible and powerful endpoint, designed for direct data manipulation and retrieval. It supports parameterized queries for safety. The `sql` field can contain any valid SQLite statement (SELECT, INSERT, UPDATE, DELETE, CREATE, etc.).

-   **Request Body:**
    ```json
    {
      "sql": "SELECT username FROM users WHERE agent_type = ?;",
      "params": ["research"]
    }
    ```
-   **Success Response (200 OK):**
    -   For `SELECT` queries:
        ```json
        {
          "data": [
            { "username": "agent_007" }
          ],
          "rows_affected": 1
        }
        ```
    -   For `INSERT`, `UPDATE`, `DELETE`, `CREATE` etc.:
        ```json
        {
          "message": "Query executed successfully.",
          "rows_affected": 1
        }
        ```
-   **Error Response (400 Bad Request):** For invalid SQL syntax.
    ```json
    {
      "error": {
        "code": "BAD_REQUEST",
        "message": "SQL Error: ...",
        "status": 400
      }
    }
    ```
-   **Error Response (404 Not Found):** If `db_name` does not exist.
    ```json
    {
      "error": {
        "code": "NOT_FOUND",
        "message": "Database not found.",
        "status": 404
      }
    }
    ```

### `POST /api/db/{db_name}/tables`

A convenience endpoint to create a new table.

-   **Request Body:**
    ```json
    {
      "table_name": "tasks",
      "columns": [
        {"name": "id", "type": "INTEGER", "primary_key": true},
        {"name": "description", "type": "TEXT", "not_null": true},
        {"name": "status", "type": "TEXT", "default": "pending"}
      ]
    }
    ```
-   **Success Response (201 Created):**
    ```json
    {
      "message": "Table 'tasks' created successfully."
    }
    ```

### `GET /api/db/{db_name}/tables/{table_name}/rows`

Selects rows from a table. URL query parameters are used for simple `WHERE key = value` clauses.

-   **Example Request:** `GET /api/db/my_db/tasks/rows?status=pending`
-   **Success Response (200 OK):**
    ```json
    {
      "data": [
        { "id": 1, "description": "Analyze market trends", "status": "pending" }
      ],
      "rows_affected": 1
    }
    ```

### `POST /api/db/{db_name}/tables/{table_name}/rows`

Inserts one or more rows into a table.

-   **Request Body:**
    ```json
    {
      "rows": [
        {"description": "Task 1", "status": "wip"},
        {"description": "Task 2"}
      ]
    }
    ```
-   **Success Response (201 Created):**
    ```json
    {
      "message": "Rows inserted successfully.",
      "rows_affected": 2
    }
    ```
