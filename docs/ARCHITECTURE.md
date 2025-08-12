# Praetorian DB-Forge: Architecture Deep Dive

This document provides a more detailed overview of the Praetorian DB-Forge system's architecture, component interactions, and design principles.

## Core Components

The Praetorian DB-Forge system is composed of several key components that work together to provide a containerized DBaaS solution.

### 1. DB Worker Base (`db-worker-base`)

*   **Purpose:** Serves as the lightweight, minimal base image for all dynamically spawned database instances.
*   **Technology:** Built on `alpine:latest` and includes the `sqlite3` command-line tool.
*   **Functionality:** These containers are designed to be simple, ephemeral processes that primarily act as holders for the SQLite database files. They do not run a database server; instead, the `db-gateway` directly interacts with the SQLite files mounted within its own volume.
*   **Design Principle:** Minimal footprint, fast startup, and isolation for each database instance.

### 2. DB Gateway (`db-gateway`)

*   **Purpose:** The central application responsible for orchestrating database instances and handling all data plane operations.
*   **Technology:** Developed using FastAPI (Python) for its asynchronous capabilities and robust API development features. It uses the `docker` Python library to interact with the Docker daemon and `aiosqlite` for asynchronous SQLite database operations.
*   **Roles:**
    *   **Orchestrator:** Manages the lifecycle of database instances. This includes:
        *   **Spawning:** Dynamically creating new `db-worker` containers.
        *   **Pruning:** Stopping and removing `db-worker` containers.
        *   **Listing:** Providing a list of all active database instances.
        *   **Data Volume Management:** The `db-gateway` container has a bind mount (`./db-data` from host to `/databases` in container) where all SQLite database files (`.db`) are stored. This ensures data persistence independent of the `db-worker` container's lifecycle.
    *   **Data Plane:** Exposes a RESTful API for interacting with the data inside specific databases. This includes:
        *   **Raw SQL Query Execution:** Allows execution of any valid SQL statement, including parameterized queries.
        *   **Schema Manipulation:** Convenience endpoints for creating tables.
        *   **Data Manipulation:** Endpoints for inserting and retrieving rows.
*   **Interactions:** The `db-gateway` communicates with the Docker daemon via its mounted `docker.sock` to manage `db-worker` containers. It directly accesses and modifies SQLite database files within its `/databases` volume.

### 3. Traefik Reverse Proxy

*   **Purpose:** Provides a unified, intelligent entry point for all external traffic to the DB-Forge services.
*   **Technology:** Traefik v2.x.
*   **Functionality:** Automatically discovers services (like `db-gateway`) via Docker labels and routes incoming HTTP requests to the correct service. It handles SSL termination (though not configured by default in this setup) and load balancing.
*   **Configuration:** Configured via `infra/traefik/traefik.yml` and Docker labels on the `db-gateway` service in `docker-compose.yml`.

## Data Flow

1.  **Client Request:** A client (e.g., `client.sh`, a web application, or an AI agent) sends an HTTP request to `http://db.localhost` (or the configured domain).
2.  **Traefik Routing:** Traefik receives the request, identifies the `db-gateway` service based on its Docker labels, and forwards the request to the `db-gateway` container.
3.  **DB Gateway Processing:**
    *   **Admin Requests:** If the request is for an `/admin` endpoint, the `db-gateway` interacts with the Docker daemon to manage `db-worker` containers (spawn, prune, list).
    *   **Data Requests:** If the request is for a `/api/db/{db_name}` endpoint, the `db-gateway` identifies the target database file within its `/databases` volume. It then uses `aiosqlite` to execute the SQL query against that specific `.db` file.
4.  **Response:** The `db-gateway` processes the query results and returns an HTTP response (typically JSON) back through Traefik to the client.

## Design Principles

*   **Self-Hosted & Sovereign:** All components are designed to run locally, giving users full control over their data and infrastructure.
*   **API-First:** All interactions are exposed via a clean, RESTful API, making it easy for programmatic access and integration with other systems.
*   **Containerization:** Leveraging Docker for isolation, portability, and simplified deployment.
*   **Modularity:** Components are loosely coupled, allowing for independent development and future extensibility (e.g., adding new database backends).
*   **Simplicity:** Prioritizing straightforward solutions, especially with the initial SQLite backend, to reduce complexity.
