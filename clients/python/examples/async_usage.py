#!/usr/bin/env python3
"""Async usage example for DB-Forge Python client."""

import asyncio
import os
from dbforge_client import AsyncDBForgeClient, DBForgeError

async def main():
    """Demonstrate async DB-Forge operations."""
    
    db_name = "async_example_db"
    
    # Use async context manager for proper cleanup
    async with AsyncDBForgeClient(
        base_url=os.getenv("DBFORGE_BASE_URL", "http://db.localhost"),
        api_key=os.getenv("DBFORGE_API_KEY"),
    ) as client:
        
        try:
            print("=== DB-Forge Async Python Client Example ===\n")
            
            # 1. Health check
            print("1. Health check:")
            health = await client.health_check()
            print(f"   Health: {health}")
            
            # 2. Spawn database
            print(f"\n2. Spawning database: {db_name}")
            spawn_result = await client.spawn_database(db_name)
            print(f"   Result: {spawn_result}")
            
            # 3. Get database instance
            print(f"\n3. Getting database instance: {db_name}")
            db = client.get_database(db_name)
            
            # 4. Create tables concurrently
            print("\n4. Creating tables concurrently:")
            
            users_task = db.create_table("users", [
                {"name": "id", "type": "INTEGER", "primary_key": True},
                {"name": "name", "type": "TEXT", "not_null": True},
                {"name": "email", "type": "TEXT", "not_null": True}
            ])
            
            products_task = db.create_table("products", [
                {"name": "id", "type": "INTEGER", "primary_key": True},
                {"name": "name", "type": "TEXT", "not_null": True},
                {"name": "price", "type": "REAL", "not_null": True}
            ])
            
            orders_task = db.create_table("orders", [
                {"name": "id", "type": "INTEGER", "primary_key": True},
                {"name": "user_id", "type": "INTEGER", "not_null": True},
                {"name": "product_id", "type": "INTEGER", "not_null": True},
                {"name": "quantity", "type": "INTEGER", "default": "1"},
                {"name": "order_date", "type": "DATETIME", "default": "CURRENT_TIMESTAMP"}
            ])
            
            # Wait for all tables to be created
            table_results = await asyncio.gather(
                users_task, products_task, orders_task
            )
            
            for i, result in enumerate(table_results, 1):
                print(f"   Table {i}: {result}")
            
            # 5. Insert data concurrently
            print("\n5. Inserting data concurrently:")
            
            users_insert = db.insert_rows("users", [
                {"name": "Alice Johnson", "email": "alice@example.com"},
                {"name": "Bob Smith", "email": "bob@example.com"},
                {"name": "Charlie Brown", "email": "charlie@example.com"}
            ])
            
            products_insert = db.insert_rows("products", [
                {"name": "Laptop", "price": 999.99},
                {"name": "Mouse", "price": 29.99},
                {"name": "Keyboard", "price": 79.99},
                {"name": "Monitor", "price": 299.99}
            ])
            
            insert_results = await asyncio.gather(users_insert, products_insert)
            for i, result in enumerate(insert_results, 1):
                print(f"   Insert {i}: {result}")
            
            # 6. Insert orders
            print("\n6. Inserting orders:")
            orders_result = await db.insert_rows("orders", [
                {"user_id": 1, "product_id": 1, "quantity": 1},  # Alice buys laptop
                {"user_id": 1, "product_id": 2, "quantity": 2},  # Alice buys 2 mice
                {"user_id": 2, "product_id": 3, "quantity": 1},  # Bob buys keyboard
                {"user_id": 3, "product_id": 4, "quantity": 1},  # Charlie buys monitor
            ])
            print(f"   Orders: {orders_result}")
            
            # 7. Query data concurrently
            print("\n7. Querying data concurrently:")
            
            users_query = db.select_rows("users")
            products_query = db.select_rows("products")
            expensive_products_query = db.execute_query(
                "SELECT * FROM products WHERE price > ?", [100]
            )
            
            query_results = await asyncio.gather(
                users_query, products_query, expensive_products_query
            )
            
            print(f"   Users: {query_results[0]}")
            print(f"   Products: {query_results[1]}")
            print(f"   Expensive products: {query_results[2]}")
            
            # 8. Complex analytics query
            print("\n8. Running analytics query:")
            analytics = await db.execute_query("""
                SELECT 
                    u.name as customer,
                    u.email,
                    COUNT(o.id) as order_count,
                    SUM(p.price * o.quantity) as total_spent
                FROM users u
                LEFT JOIN orders o ON u.id = o.user_id
                LEFT JOIN products p ON o.product_id = p.id
                GROUP BY u.id, u.name, u.email
                ORDER BY total_spent DESC
            """)
            
            print("   Customer analytics:")
            for row in analytics.get("data", []):
                print(f"     {row}")
            
            # 9. Batch operations
            print("\n9. Performing batch operations:")
            
            # Create multiple queries to run in parallel
            batch_queries = [
                db.execute_query("SELECT COUNT(*) as user_count FROM users"),
                db.execute_query("SELECT COUNT(*) as product_count FROM products"),
                db.execute_query("SELECT COUNT(*) as order_count FROM orders"),
                db.execute_query("SELECT AVG(price) as avg_price FROM products"),
                db.execute_query("SELECT MAX(price) as max_price FROM products"),
                db.execute_query("SELECT MIN(price) as min_price FROM products"),
            ]
            
            batch_results = await asyncio.gather(*batch_queries)
            
            stats = {}
            stats.update(batch_results[0])  # user_count
            stats.update(batch_results[1])  # product_count  
            stats.update(batch_results[2])  # order_count
            stats.update(batch_results[3])  # avg_price
            stats.update(batch_results[4])  # max_price
            stats.update(batch_results[5])  # min_price
            
            print(f"   Database statistics: {stats}")
            
            # 10. List all databases
            print("\n10. Listing all databases:")
            databases = await client.list_databases()
            for database in databases:
                print(f"    - {database}")
            
            print(f"\n=== Cleanup ===")
            # 11. Cleanup
            print(f"11. Pruning database: {db_name}")
            prune_result = await client.prune_database(db_name)
            print(f"    Result: {prune_result}")
            
            print("\n✅ Async example completed successfully!")
            
        except DBForgeError as e:
            print(f"❌ DB-Forge error: {e}")
            print(f"   Status code: {e.status_code}")
            print(f"   Error code: {e.error_code}")
            return 1
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return 1
    
    return 0


def run_async_example():
    """Run the async example."""
    return asyncio.run(main())


if __name__ == "__main__":
    exit(run_async_example())