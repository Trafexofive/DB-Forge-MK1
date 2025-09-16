from fastapi import APIRouter, Depends, HTTPException, status
from auth.auth import verify_api_key_header
from providers.database import get_docker_client, get_worker_name, spawn_database_container, get_database_containers
from services.database import is_valid_db_name
from models.database import SpawnResponse, PruneResponse, DBInstance
import docker

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(verify_api_key_header)]
)

@router.post("/databases/spawn/{db_name}", response_model=SpawnResponse, status_code=status.HTTP_201_CREATED)
async def spawn_database(db_name: str):
    """
    Spawns a new, isolated database instance.
    
    This endpoint creates a new Docker container running a `db-worker` image, 
    which holds an SQLite database file. If an instance with the given name 
    already exists and is running, the request is idempotent and will return 
    a success message. If the instance exists but is stopped, it will be started.
    
    The database file is created on the host filesystem and mounted into the worker.
    This ensures data persists beyond the container lifecycle.
    
    Args:
        db_name (str): A unique name for the database. Must be filesystem and Docker-name friendly.
        
    Returns:
        SpawnResponse: Details about the spawned or existing database instance.
        
    Raises:
        HTTPException:
            - 400: If the `db_name` is invalid.
            - 503: If the Docker daemon is not available.
    """
    if not is_valid_db_name(db_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid database name.")
    
    docker_client = get_docker_client()
    worker_name = get_worker_name(db_name)
    
    try:
        container = docker_client.containers.get(worker_name)
        if container.status == "exited":
            container.start()
        return SpawnResponse(
            message="Database instance already exists and is running.",
            db_name=db_name,
            container_id=container.id,
        )
    except docker.errors.NotFound:
        container = spawn_database_container(docker_client, db_name)
        return SpawnResponse(
            message="Database instance spawned successfully.",
            db_name=db_name,
            container_id=container.id,
        )

@router.post("/databases/prune/{db_name}", response_model=PruneResponse)
async def prune_database(db_name: str):
    """Stops and removes a specific database instance container."""
    docker_client = get_docker_client()
    worker_name = get_worker_name(db_name)
    
    try:
        container = docker_client.containers.get(worker_name)
        container.stop()
        container.remove()
        return PruneResponse(message="Database instance pruned successfully.", db_name=db_name)
    except docker.errors.NotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database instance not found.")

@router.get("/databases", response_model=list[DBInstance])
async def list_databases():
    """Lists all currently managed database instances."""
    docker_client = get_docker_client()
    instances = []
    containers = get_database_containers(docker_client)
    
    for c in containers:
        db_name = c.labels.get("db-name", "unknown")
        instances.append(DBInstance(name=db_name, container_id=c.id, status=c.status))
    return instances