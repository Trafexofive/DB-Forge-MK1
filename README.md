# Praetorian DB-Forge

Praetorian DB-Forge is a containerized Database-as-a-Service (DBaaS) platform that simplifies managing isolated database instances. It provides a RESTful API to dynamically create, manage, and interact with individual databases. Built with SQLite as the initial backend, it prioritizes ease of use, portability, and direct control over your data.

## Key Features

*   **Dynamic Database Provisioning:** Spin up or tear down isolated database environments with simple API calls.
*   **Persistent Data:** Each database's data is stored directly on your host filesystem, ensuring it remains safe and accessible even if containers are removed or restarted.
*   **RESTful API:** Interact with your databases using a straightforward HTTP API for common operations like CRUD, schema changes, and raw SQL queries.
*   **Isolated Instances:** Every database runs in its own dedicated Docker container, providing clear separation and preventing conflicts.
*   **Extensible Design:** The architecture is designed to easily support other database backends (like PostgreSQL) in the future.

## Architecture

The system consists of two main parts:

1.  **DB Worker Base (`db-worker-base`):** A minimal Docker image (based on `alpine:latest` with `sqlite3`) that serves as a lightweight template for each database instance. These workers essentially act as containers for your database files.
2.  **DB Gateway (`db-gateway`):** A FastAPI application that acts as the central hub. It handles:
    *   **Database Management:** API endpoints to create, remove, and list database instances.
    *   **Data Operations:** Translates your HTTP requests into SQL commands, executes them against the appropriate database files (which are mounted from your host), and returns results as JSON.

All external network traffic is managed by a Traefik reverse proxy, providing a single entry point to the DB-Forge services.

## Getting Started

All common development and deployment tasks are automated using the `Makefile`.

### Prerequisites

Make sure you have the following installed:

*   [Docker](https://docs.docker.com/get-docker/)
*   [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Configure Your Environment

Copy the example environment file and adjust any settings as needed:

```bash
cp .env.example .env
```

### 2. Start the Services

This command builds the necessary Docker images and starts the DB Gateway and Traefik proxy:

```bash
make up
```

### 3. Access the API

The DB Gateway is accessible via Traefik. By default, it routes traffic to `http://db.localhost`.
For detailed API endpoints and usage examples, refer to `docs/API.md`.

## Testing

The project includes a comprehensive suite of API tests to verify functionality.

To run the tests, ensure your Docker stack is running (`make up`), then execute:

```bash
make test
```

This command will:
*   Clean up any test databases from previous runs.
*   Restart the `db-gateway` service to ensure a fresh state.
*   Execute the API test suite against the running gateway.

## Cleanup

To shut down the entire stack and remove all associated containers, networks, and persistent data:

```bash
make clean
```

**⚠️ WARNING:** The `make clean` command will **permanently delete all database files** stored in the `db-data/` directory. Use with caution.

## Contributing

Contributions are welcome! Please refer to our (future) `CONTRIBUTING.md` for guidelines.

## License

This project is licensed under the [MIT License](LICENSE).
