# Praetorian DB-Forge API Specification

This document defines the RESTful API contract for interacting with the DB-Forge gateway.

**Base URL:** `http://db.localhost` (or as defined in `.env`)

## Error Responses

All error responses from the API follow a standardized JSON format:

```json
{
  "error": {
    "code": "MACHINE_READABLE_CODE",
    "message": "Human readable description of the error.",
    "status": 404 // The corresponding HTTP status code
  }
}
```

Specific error examples are provided in the endpoint sections below.

---

## 1. Admin API (Orchestrator)

These endpoints are for managing the lifecycle of database instances.

### `POST /admin/databases/spawn/{db_name}`

Spawns a new, isolated SQLite database instance. This action is idempotent; if an instance already exists, it will ensure it is running. The database data is stored in a file on the host filesystem (`./db-data/{db_name}.db`), ensuring persistence and data sovereignty. A lightweight Docker container (`db-worker`) is created to hold this database file.

-   **URL Params:**
    -   `db_name` (string, required): A unique name for the database (e.g., `agent-alpha-memory`). Must be filesystem and Docker-name friendly.
-   **Success Response (201 Created or 200 OK):**
    ```json
    {
      "message": "Database instance spawned successfully.",
      "db_name": "agent-alpha-memory",
      "container_id": "a1b2c3d4e5f6..."
    }
    ```
-   **Error Response (400 Bad Request):** If `db_name` is invalid.
    ```json
    {
      "error": {
        "code": "BAD_REQUEST",
        "message": "Invalid database name.",
        "status": 400
      }
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
