#!/usr/bin/env python3
"""Basic usage example for DB-Forge Python client."""

import os
from dbforge_client import DBForgeClient, DBForgeError

def main():
    """Demonstrate basic DB-Forge operations."""
    
    # Initialize client
    client = DBForgeClient(
        base_url=os.getenv("DBFORGE_BASE_URL", "http://db.localhost"),
        api_key=os.getenv("DBFORGE_API_KEY"),  # Optional
    )
    
    db_name = "example_app_db"
    new_db = client.spawn_database(db_name)
    
    try:
        print("=== DB-Forge Python Client Example ===\n")
        
        # 1. Spawn a new database
        print(f"1. Spawning database: {db_name}")
        spawn_result = client.spawn_database(db_name)
        print(f"   Result: {spawn_result}")
        
        # 2. List databases
        print("\n2. Listing databases:")
        databases = client.list_databases()
        for db in databases:
            print(f"   - {db['name']} (status: {db['status']})")
        
        # 3. Get database instance for operations
        print(f"\n3. Getting database instance: {db_name}")
        db = client.get_database(db_name)
        
        # 4. Create a table
        print("\n4. Creating users table:")
        table_result = db.create_table("users", [
            {"name": "id", "type": "INTEGER", "primary_key": True},
            {"name": "username", "type": "TEXT", "not_null": True, "unique": True},
            {"name": "email", "type": "TEXT", "not_null": True},
            {"name": "created_at", "type": "DATETIME", "default": "CURRENT_TIMESTAMP"},
            {"name": "is_active", "type": "BOOLEAN", "default": "1"}
        ])
        print(f"   Result: {table_result}")
        
        # 5. Insert some data
        print("\n5. Inserting user data:")
        insert_result = db.insert_rows("users", [
            {"username": "alice", "email": "alice@example.com"},
            {"username": "bob", "email": "bob@example.com"},
            {"username": "charlie", "email": "charlie@example.com"}
        ])
        print(f"   Result: {insert_result}")
        
        # 6. Query data using select_rows
        print("\n6. Querying all users:")
        all_users = db.select_rows("users")
        for user in all_users:
            print(f"   - {user}")
        
        # 7. Query with filters
        print("\n7. Querying specific user:")
        alice = db.select_rows("users", {"username": "alice"})
        print(f"   Alice: {alice}")
        
        # 8. Raw SQL query
        print("\n8. Raw SQL query - user count:")
        count_result = db.execute_query("SELECT COUNT(*) as user_count FROM users")
        print(f"   Count result: {count_result}")
        
        # 9. Update data using raw SQL
        print("\n9. Updating user status:")
        update_result = db.execute_query(
            "UPDATE users SET is_active = ? WHERE username = ?",
            [0, "charlie"]
        )
        print(f"   Update result: {update_result}")
        
        # 10. Verify update
        print("\n10. Verifying update:")
        charlie = db.select_rows("users", {"username": "charlie"})
        print(f"    Charlie after update: {charlie}")
        
        # 11. List tables
        print("\n11. Listing tables:")
        tables = db.list_tables()
        print(f"    Tables: {tables}")
        
        # 12. Get table schema
        print("\n12. Getting users table schema:")
        schema = db.get_table_schema("users")
        for column in schema:
            print(f"    Column: {column}")
        
        # 13. Advanced query with JOIN (create related table first)
        print("\n13. Creating posts table for JOIN example:")
        db.create_table("posts", [
            {"name": "id", "type": "INTEGER", "primary_key": True},
            {"name": "user_id", "type": "INTEGER", "not_null": True},
            {"name": "title", "type": "TEXT", "not_null": True},
            {"name": "content", "type": "TEXT"}
        ])
        
        # Insert some posts
        db.insert_rows("posts", [
            {"user_id": 1, "title": "Alice's First Post", "content": "Hello world!"},
            {"user_id": 1, "title": "Alice's Second Post", "content": "More content"},
            {"user_id": 2, "title": "Bob's Post", "content": "Bob here!"}
        ])
        
        # Query with JOIN
        print("\n14. JOIN query - users and their posts:")
        join_result = db.execute_query("""
            SELECT u.username, u.email, p.title, p.content
            FROM users u
            JOIN posts p ON u.id = p.user_id
            ORDER BY u.username, p.id
        """)
        for row in join_result.get("data", []):
            print(f"    {row}")
        
        print(f"\n=== Cleanup ===")
        # 15. Cleanup - prune the database
        print(f"15. Pruning database: {db_name}")
        prune_result = client.prune_database(db_name)
        print(f"    Result: {prune_result}")
        
        print("\n✅ Example completed successfully!")
        
    except DBForgeError as e:
        print(f"❌ DB-Forge error: {e}")
        print(f"   Status code: {e.status_code}")
        print(f"   Error code: {e.error_code}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
