# Praetorian DB-Forge

**Forged by Gemini in accordance with the Himothy Covenant.**

Praetorian DB-Forge is a highly available, containerized Database-as-a-Service (DBaaS) platform designed for AI agents and automated systems. It provides a robust RESTful API gateway for dynamically spawning, managing, and interacting with isolated database instances. The initial implementation leverages SQLite for its portability, simplicity, and emphasis on data sovereignty.

## ✨ Key Features

*   **Dynamic Database Provisioning:** Create and destroy isolated database environments with simple API calls.
*   **Absolute Data Sovereignty:** Each database's data is persistently stored on the host filesystem, ensuring full ownership and data survival across container lifecycles.
*   **RESTful Data Access:** A comprehensive API for all common database operations (CRUD, schema manipulation, raw queries).
*   **Container-Level Multi-tenancy:** Each database instance operates in its own isolated Docker container, guaranteeing separation and preventing cross-contamination.
*   **Pluggable Backend Design:** Architected for future extensibility to support various database backends beyond SQLite.

## 🏗️ Architecture Overview

The system comprises two main components:

1.  **DB Worker Base (`db-worker-base`):** A minimal Docker image (`alpine:latest` with `sqlite3`) serving as a lightweight template for all spawned database instances. These workers act as data volume holders.
2.  **DB Gateway (`db-gateway`):** The core FastAPI application that functions as both:
    *   **Orchestrator:** Manages the lifecycle of database instances (spawn, prune, list) via administrative endpoints.
    *   **Data Plane:** Translates HTTP requests into SQL commands, executes them against the appropriate database files (stored on a mounted volume), and returns results as JSON.

All external traffic is routed through a Traefik reverse proxy, providing a unified entry point.

## 🚀 Getting Started

All primary operations are managed via the `Makefile`.

### Prerequisites

Ensure you have the following installed:

*   [Docker](https://docs.docker.com/get-docker/)
*   [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Configure Your Environment

Copy the example environment file and customize it as needed.

```bash
cp .env.example .env
```

### 2. Ignite the Forge

This command builds the necessary Docker images and starts the DB Gateway and Traefik proxy.

```bash
make up
```

### 3. Access the API

The DB Gateway is accessible via Traefik. By default, it routes traffic to `http://db.localhost`.
Refer to `docs/API.md` for the complete API specification and usage examples.

## 🧪 Testing

The project includes a comprehensive suite of API tests to ensure functionality and stability.

To run the tests, ensure your Docker stack is up (`make up`), then execute:

```bash
make test
```

This command will:
*   Clean up any leftover test databases from previous runs.
*   Restart the `db-gateway` service to ensure a clean state.
*   Execute the API test suite, interacting with the running gateway.

## 🧹 Cleanup

To shut down the stack and remove all associated containers, networks, and persistent data volumes:

```bash
make clean
```

**⚠️ WARNING:** The `make clean` command will **permanently delete all database files** stored in the `db-data/` directory. Use with caution.

## 🤝 Contributing

Contributions are welcome! Please refer to our (future) `CONTRIBUTING.md` for guidelines.

## 📄 License

This project is licensed under the [MIT License](LICENSE).