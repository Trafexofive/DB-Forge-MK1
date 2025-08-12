import httpx
import pytest
import asyncio
import os

# Base URL for the DB Gateway, as routed by Traefik
BASE_URL = "http://db.localhost"

# Ensure the Docker stack is up before running tests
@pytest.fixture(scope="module", autouse=True)
def setup_docker_stack():
    # This fixture assumes the stack is already up from previous steps
    # In a real CI/CD, you might run 'make up' here
    print("\nEnsuring Docker stack is running...")
    # Basic check to see if the gateway is reachable
    try:
        response = httpx.get(f"{BASE_URL}/", timeout=5)
        response.raise_for_status()
        print("DB Gateway is reachable.")
    except httpx.RequestError as e:
        pytest.fail(f"DB Gateway not reachable at {BASE_URL}. Is the Docker stack up? Error: {e}")
    except httpx.HTTPStatusError as e:
        pytest.fail(f"DB Gateway returned an error status: {e.response.status_code}. Is the Docker stack up? Error: {e}")

    yield

    print("\nTests finished. Cleaning up spawned databases...")
    # Clean up any databases that might have been left behind
    asyncio.run(cleanup_databases())

async def cleanup_databases():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/admin/databases")
            response.raise_for_status()
            databases = response.json()
            for db in databases:
                print(f"Pruning database: {db['name']}")
                await client.post(f"{BASE_URL}/admin/databases/prune/{db['name']}")
        except httpx.RequestError as e:
            print(f"Warning: Could not connect to DB Gateway for cleanup: {e}")
        except httpx.HTTPStatusError as e:
            print(f"Warning: DB Gateway returned error during cleanup: {e.response.status_code} - {e.response.text}")

@pytest.mark.asyncio
async def test_root_endpoint():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
        assert response.status_code == 200
        assert response.json() == {"message": "Praetorian DB-Forge is online."}

@pytest.mark.asyncio
async def test_spawn_database():
    db_name = "test_db_spawn"
    async with httpx.AsyncClient() as client:
        # Test initial spawn
        response = await client.post(f"{BASE_URL}/admin/databases/spawn/{db_name}")
        assert response.status_code == 201
        assert response.json()["message"] == "Database instance spawned successfully."
        assert response.json()["db_name"] == db_name
        assert "container_id" in response.json()

        # Test idempotency
        response = await client.post(f"{BASE_URL}/admin/databases/spawn/{db_name}")
        assert response.status_code == 200
        assert response.json()["message"] == "Database instance already exists and is running."
        assert response.json()["db_name"] == db_name

@pytest.mark.asyncio
async def test_list_databases():
    db_name_1 = "test_db_list_1"
    db_name_2 = "test_db_list_2"
    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE_URL}/admin/databases/spawn/{db_name_1}")
        await client.post(f"{BASE_URL}/admin/databases/spawn/{db_name_2}")

        response = await client.get(f"{BASE_URL}/admin/databases")
        assert response.status_code == 200
        databases = response.json()
        db_names = [db["name"] for db in databases]
        assert db_name_1 in db_names
        assert db_name_2 in db_names

@pytest.mark.asyncio
async def test_prune_database():
    db_name = "test_db_prune"
    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE_URL}/admin/databases/spawn/{db_name}")
        
        response = await client.post(f"{BASE_URL}/admin/databases/prune/{db_name}")
        assert response.status_code == 200
        assert response.json()["message"] == "Database instance pruned successfully."
        assert response.json()["db_name"] == db_name

        # Verify it's no longer listed
        response = await client.get(f"{BASE_URL}/admin/databases")
        databases = response.json()
        db_names = [db["name"] for db in databases]
        assert db_name not in db_names

        # Test pruning non-existent DB
        response = await client.post(f"{BASE_URL}/admin/databases/prune/non_existent_db")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_table_and_insert_data():
    db_name = "test_db_data"
    table_name = "users"
    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE_URL}/admin/databases/spawn/{db_name}")

        # Create table
        create_table_payload = {
            "table_name": table_name,
            "columns": [
                {"name": "id", "type": "INTEGER", "primary_key": True},
                {"name": "name", "type": "TEXT", "not_null": True},
                {"name": "age", "type": "INTEGER"}
            ]
        }
        response = await client.post(f"{BASE_URL}/api/db/{db_name}/tables", json=create_table_payload)
        assert response.status_code == 201
        assert response.json()["message"] == f"Table '{table_name}' created successfully."

        # Insert data
        insert_payload = {
            "rows": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 24}
            ]
        }
        response = await client.post(f"{BASE_URL}/api/db/{db_name}/tables/{table_name}/rows", json=insert_payload)
        assert response.status_code == 201
        assert response.json()["message"] == "Rows inserted successfully."
        assert response.json()["rows_affected"] == 2

        # Query data
        response = await client.get(f"{BASE_URL}/api/db/{db_name}/tables/{table_name}/rows")
        assert response.status_code == 200
        assert response.json()["rows_affected"] == 2
        assert len(response.json()["data"]) == 2
        assert response.json()["data"][0]["name"] == "Alice"

        # Query with filter
        response = await client.get(f"{BASE_URL}/api/db/{db_name}/tables/{table_name}/rows?age=24")
        assert response.status_code == 200
        assert response.json()["rows_affected"] == 1
        assert response.json()["data"][0]["name"] == "Bob"

@pytest.mark.asyncio
async def test_raw_sql_queries():
    db_name = "test_db_raw_sql"
    table_name = "products"
    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE_URL}/admin/databases/spawn/{db_name}")

        # Create table using raw SQL
        await client.post(f"{BASE_URL}/api/db/{db_name}/query", json={
            "sql": f"CREATE TABLE '{table_name}' (id INTEGER PRIMARY KEY, name TEXT, price REAL)"
        })

        # Insert data using raw SQL
        response = await client.post(f"{BASE_URL}/api/db/{db_name}/query", json={
            "sql": f"INSERT INTO '{table_name}' (name, price) VALUES (?, ?)",
            "params": ["Laptop", 1200.50]
        })
        assert response.status_code == 200
        assert response.json()["rows_affected"] == 1

        response = await client.post(f"{BASE_URL}/api/db/{db_name}/query", json={
            "sql": f"INSERT INTO '{table_name}' (name, price) VALUES (?, ?)",
            "params": ["Mouse", 25.00]
        })
        assert response.status_code == 200
        assert response.json()["rows_affected"] == 1

        # Select data using raw SQL
        response = await client.post(f"{BASE_URL}/api/db/{db_name}/query", json={
            "sql": f"SELECT * FROM '{table_name}' WHERE price > ?",
            "params": [100]
        })
        assert response.status_code == 200
        assert response.json()["rows_affected"] == 1
        assert response.json()["data"][0]["name"] == "Laptop"

        # Update data using raw SQL
        response = await client.post(f"{BASE_URL}/api/db/{db_name}/query", json={
            "sql": f"UPDATE '{table_name}' SET price = ? WHERE name = ?",
            "params": [1100.00, "Laptop"]
        })
        assert response.status_code == 200
        assert response.json()["rows_affected"] == 1

        # Verify update
        response = await client.post(f"{BASE_URL}/api/db/{db_name}/query", json={
            "sql": f"SELECT price FROM '{table_name}' WHERE name = ?",
            "params": ["Laptop"]
        })
        assert response.status_code == 200
        assert response.json()["data"][0]["price"] == 1100.0

        # Delete data using raw SQL
        response = await client.post(f"{BASE_URL}/api/db/{db_name}/query", json={
            "sql": f"DELETE FROM '{table_name}' WHERE name = ?",
            "params": ["Mouse"]
        })
        assert response.status_code == 200
        assert response.json()["rows_affected"] == 1

        # Test SQL error handling
        response = await client.post(f"{BASE_URL}/api/db/{db_name}/query", json={
            "sql": "SELECT * FROM non_existent_table"
        })
        assert response.status_code == 400
        assert "SQL Error" in response.json()["detail"]

@pytest.mark.asyncio
async def test_data_plane_db_not_found():
    db_name = "non_existent_db_for_data_plane"
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/api/db/{db_name}/query", json={
            "sql": "SELECT 1"
        })
        assert response.status_code == 404
        assert response.json()["detail"] == "Database not found."

        response = await client.post(f"{BASE_URL}/api/db/{db_name}/tables", json={
            "table_name": "test", "columns": []
        })
        assert response.status_code == 404
        assert response.json()["detail"] == "Database not found."

        response = await client.get(f"{BASE_URL}/api/db/{db_name}/tables/some_table/rows")
        assert response.status_code == 404
        assert response.json()["detail"] == "Database not found."

        response = await client.post(f"{BASE_URL}/api/db/{db_name}/tables/some_table/rows", json={
            "rows": []
        })
        assert response.status_code == 404
        assert response.json()["detail"] == "Database not found."

