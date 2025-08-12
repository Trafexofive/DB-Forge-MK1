# Praetorian DB-Forge

**Forged by Gemini in accordance with the Himothy Covenant.**

Praetorian DB-Forge is a highly available, containerized database-as-a-service (DBaaS) platform. It provides a RESTful API gateway that dynamically spawns, manages, and interacts with isolated database instances. It is designed from the ground up to serve as a persistent memory and structured data tool for AI agents and other automated systems.

The initial implementation uses SQLite for maximum portability, simplicity, and data sovereignty.

## I. The Architecture of the Forge

The system is comprised of two primary components:

1.  **DB Worker Base (`db-worker-base`):** A minimal Docker image containing the necessary tools (e.g., `sqlite3`). This image is used as a template for all spawned database instances.

2.  **DB Gateway (`db-gateway`):** The core of the DB-Forge. This FastAPI application serves two purposes:
    *   **Orchestrator:** It exposes administrative endpoints (`/admin/databases`) to spawn, prune, and list database instances. Each instance is a separate Docker container with its own dedicated, persistent volume for data storage.
    *   **Data Plane:** It provides a generic, RESTful API (`/api/db/{db_name}`) to interact with the databases. It translates HTTP requests into SQL commands, executes them against the appropriate database file, and returns the results as JSON.

### Key Features:

-   **Dynamic Database Provisioning:** Spawn or destroy fully isolated database environments with single API calls.
-   **Data Persistence:** Each database's data is stored in a dedicated Docker volume, ensuring data survives container restarts.
-   **RESTful Data Access:** A comprehensive REST API for all common database operations (CRUD, schema manipulation, raw queries).
-   **Multi-tenancy:** Each database is completely isolated at the container and filesystem level.
-   **Pluggable by Design:** Architected to support different database backends in the future.

## II. The Forging Process (Deployment)

All commands are executed via the Master Control Program (`Makefile`).

### Prerequisites

-   Docker & Docker Compose

### 1. Configure the Environment

Copy `.env.example` to `.env` and modify as needed.

```bash
cp .env.example .env
```

### 2. Ignite the Forge

This command builds the necessary images and starts the DB Gateway and Traefik proxy.

```bash
make up
```

## III. Interacting with the Oracle (API Usage)

All API interactions are directed to the DB Gateway. By default, Traefik routes `http://db.localhost` to this service. See `docs/API.md` for the full API specification.
