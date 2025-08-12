# Praetorian DB-Forge

**Forged by Gemini, your Master Systems Consultant.**

Praetorian DB-Forge is a containerized Database-as-a-Service (DBaaS) platform designed to give you direct, simplified control over isolated database instances. It provides a robust RESTful API to dynamically create, manage, and interact with individual databases. Built with SQLite as the initial backend, it prioritizes ease of use, portability, and absolute data sovereignty.

## 🌟 Project Vision

Our vision for Praetorian DB-Forge is to empower developers and automated systems with a self-hosted, highly flexible, and transparent data persistence layer. We aim to reduce the friction of managing multiple database environments, allowing you to focus on building and experimenting without worrying about infrastructure complexities.

## ✨ Key Features

*   **Dynamic Database Provisioning:** Spin up or tear down isolated database environments with simple API calls. Ideal for testing, development, or ephemeral data storage.
*   **Absolute Data Sovereignty:** Your data is stored directly on your host filesystem, ensuring full ownership, easy access, and persistence across container lifecycles.
*   **RESTful API:** Interact with your databases using a straightforward HTTP API for common operations like CRUD, schema changes, and raw SQL queries. Designed for programmatic access.
*   **Isolated Instances:** Every database runs in its own dedicated Docker container, providing clear separation, preventing conflicts, and enhancing security.
*   **Extensible Design:** The architecture is designed for easy integration of other database backends (like PostgreSQL, Redis, etc.) in the future, without changing the core API.

## 🏗️ Architecture Overview

The system consists of two primary components working in concert:

1.  **DB Worker Base (`db-worker-base`):** A minimal Docker image (based on `alpine:latest` with `sqlite3`) that serves as a lightweight template for each database instance. These workers are designed to be ephemeral containers that hold your database files.
2.  **DB Gateway (`db-gateway`):
    A FastAPI application that acts as the central hub for all database operations. It handles:
    *   **Database Lifecycle Management:** API endpoints to create, remove, and list database instances.
    *   **Data Operations:** Translates your HTTP requests into SQL commands, executes them against the appropriate database files (which are mounted from your host), and returns results as JSON.

All external network traffic is managed by a Traefik reverse proxy, providing a single, intelligent entry point to the DB-Forge services.

For a more in-depth look at the system's design principles and component interactions, refer to the [Architecture Deep Dive](docs/ARCHITECTURE.md).

## 🚀 Getting Started

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
For detailed API endpoints and usage examples, refer to the [API Specification](docs/API.md).

## 🧪 Testing

The project includes a comprehensive suite of API tests to verify functionality and stability.

To run the tests, ensure your Docker stack is running (`make up`), then execute:

```bash
make test
```

This command will:
*   Clean up any test databases from previous runs.
*   Restart the `db-gateway` service to ensure a fresh state.
*   Execute the API test suite against the running gateway.

## 🧹 Cleanup

To shut down the entire stack and remove all associated containers, networks, and persistent data:

```bash
make clean
```

**⚠️ WARNING:** The `make clean` command will **permanently delete all database files** stored in the `db-data/` directory. Use with caution.

## 🗺️ Roadmap

Curious about what's next for Praetorian DB-Forge? Check out our [Project Roadmap](TODO.md) for planned features and future directions.

## 🤝 Contributing

We welcome contributions! Please refer to our [Contribution Guidelines](docs/CONTRIBUTING.md) for details on how to get involved.

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

**Further Documentation:**

*   [API Specification](docs/API.md)
*   [Architecture Deep Dive](docs/ARCHITECTURE.md)
*   [Contribution Guidelines](docs/CONTRIBUTING.md)
*   [Project Roadmap](TODO.md)