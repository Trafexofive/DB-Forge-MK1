import os

# Load configuration from environment variables
TRAEFIK_DB_DOMAIN = os.getenv("TRAEFIK_DB_DOMAIN", "db.localhost")
CHIMERA_NETWORK = os.getenv("CHIMERA_NETWORK", "db-forge-net")
DB_WORKER_IMAGE = os.getenv("DB_WORKER_IMAGE", "db-worker-base:latest")
DB_DATA_PATH = "/databases"