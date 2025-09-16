import os
import docker
from fastapi import HTTPException, status
from utils.constants import DB_WORKER_IMAGE, CHIMERA_NETWORK, DB_DATA_PATH

def get_docker_client():
    """Initialize and return a Docker client."""
    try:
        return docker.from_env()
    except docker.errors.DockerException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not connect to Docker daemon. Is it running?"
        )

def get_db_path(db_name: str) -> str:
    """Get the full path to the SQLite database file."""
    return os.path.join(DB_DATA_PATH, f"{db_name}.db")

def get_worker_name(db_name: str) -> str:
    """Get the conventional name for a worker container."""
    return f"db-worker-{db_name}"

def spawn_database_container(docker_client, db_name: str):
    """Spawn a new database container."""
    worker_name = get_worker_name(db_name)
    
    # Create DB file placeholder
    db_path = get_db_path(db_name)
    if not os.path.exists(DB_DATA_PATH):
        os.makedirs(DB_DATA_PATH)
    open(db_path, 'a').close()

    # Spawn container
    return docker_client.containers.run(
        image=DB_WORKER_IMAGE,
        name=worker_name,
        hostname=worker_name,
        detach=True,
        network=CHIMERA_NETWORK,
        labels={"db-worker": "true", "db-name": db_name},
        restart_policy={"Name": "unless-stopped"}
    )

def get_database_containers(docker_client):
    """Get all database containers."""
    return docker_client.containers.list(all=True, filters={"label": "db-worker=true"})