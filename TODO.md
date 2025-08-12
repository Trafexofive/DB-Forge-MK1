# Praetorian DB-Forge: Unreasonably Good Roadmap

This document outlines the ambitious, yet achievable, future development path for Praetorian DB-Forge, designed to amplify agent capabilities and ensure absolute data sovereignty.

## Phase 0: Current State & Immediate Next Steps (Completed/In Progress)

*   **Core DBaaS Functionality:** Dynamic spawning, pruning, and listing of isolated SQLite database instances via a RESTful API.
*   **Basic Data Plane:** Raw SQL query execution, table creation, row insertion, and simple filtered retrieval.
*   **CLI Client (`client.sh`):** Basic command-line interface for interacting with the API.
*   **API Documentation:** Comprehensive `docs/API.md` specification.
*   **Automated Testing:** Robust `scripts/test.sh` suite for API validation.
*   **Dockerized Deployment:** `docker-compose.yml` and `Makefile` for easy setup and management.
*   **Improved `client.sh` Usability:** User-friendly named commands for common operations.

## Phase I: Data Interoperability & Enhanced CLI

This phase focuses on making data easily transferable and improving the command-line experience.

*   **Data Export Capabilities:**
    *   **CSV Export:** API endpoint (`/api/db/{db_name}/export/csv`) to export table data to CSV format.
    *   **JSON Export:** API endpoint (`/api/db/{db_name}/export/json`) to export table data to JSON format.
    *   **SQL Dump Export:** API endpoint (`/api/db/{db_name}/export/sql`) to generate a full SQL dump of a database.
*   **Data Import Capabilities:**
    *   **CSV Import:** API endpoint (`/api/db/{db_name}/import/csv`) to import data from CSV into a table.
    *   **SQL Script Import:** API endpoint (`/api/db/{db_name}/import/sql`) to execute a multi-statement SQL script.
*   **Enhanced CLI (`client.sh`):**
    *   **Pretty-Printing:** Automatically format JSON responses for readability (e.g., using `jq` internally).
    *   **Interactive Mode:** A simple interactive shell for common `client.sh` commands.
    *   **Robust Error Handling:** More descriptive error messages and exit codes.
*   **Schema Inspection API:**
    *   API endpoint (`/api/db/{db_name}/schema`) to retrieve the schema of all tables or a specific table.
    *   CLI command (`client.sh schema <db_name> [table_name]`) to display database schema.

## Phase II: User Experience & Visualization (The "Display/Render Mode")

This phase aims to provide more intuitive ways for human users to interact with and visualize their data.

*   **Web-based UI (Minimalist Dashboard):**
    *   A simple, self-hostable web interface for basic database management.
    *   Features: List databases, view container status, execute simple queries, and display results in a tabular format.
    *   Visual schema browser for easy exploration of database structure.
*   **Advanced CLI Output:**
    *   **Tabular Formatting:** Display query results in well-aligned, readable tables directly in the terminal.
    *   **Colorized Output:** Use colors for status messages, errors, and different data types for improved readability.
*   **Basic Data Visualization:**
    *   CLI commands or simple dashboard widgets to generate basic charts (e.g., bar charts for counts, pie charts for distributions) from query results.

## Phase III: Advanced Features & Operational Excellence

This phase focuses on extending core capabilities and ensuring the platform is production-ready.

*   **Multi-Backend Support (Pluggable by Design):**
    *   Implement drivers for additional database systems (e.g., PostgreSQL, MySQL, Redis).
    *   API endpoint to specify the desired backend type during database spawning.
*   **Authentication & Authorization:**
    *   **API Key Management:** Secure generation and management of API keys for gateway access.
    *   **Role-Based Access Control (RBAC):** Define roles and permissions for different users/agents to control database operations.
*   **Monitoring & Metrics:**
    *   Integrate with standard monitoring tools (e.g., Prometheus, Grafana) to expose database health and performance metrics.
    *   API endpoints for basic operational metrics (e.g., active connections, query execution times, error rates).
*   **Backup & Restore:**
    *   API endpoints for on-demand database backup and restoration.
    *   Support for automated, scheduled backups to configurable storage locations.
*   **Query Optimization/Analysis:**
    *   API endpoint to provide `EXPLAIN` output for SQL queries, helping agents optimize their data access patterns.
*   **Event Logging & Auditing:**
    *   Comprehensive logging of all API interactions and database operations for auditing and debugging purposes.

## Phase IV: Agent Integration & Autonomous Operations

This ultimate phase aims to make DB-Forge an indispensable tool for truly autonomous AI agents.

*   **Agent SDKs:**
    *   Develop official SDKs (e.g., Python, TypeScript) to simplify integration for agents and external applications.
*   **Autonomous Database Management:**
    *   Enable agents to define and enforce policies for database lifecycle management (e.g., auto-prune inactive databases, auto-scale resources).
    *   Implement self-healing capabilities for database workers (e.g., auto-restart on failure, resource allocation adjustments).
*   **Semantic Query Layer:**
    *   (Highly Ambitious) Research and develop a layer that translates natural language queries into optimized SQL, allowing agents to interact with data using higher-level concepts.
*   **Knowledge Graph Integration:**
    *   Explore integration with knowledge graph technologies to provide a richer, more interconnected memory layer for agents.

This roadmap is a living document and will evolve based on community feedback, technological advancements, and the ever-unreasonable imperative to achieve brutal mastery.