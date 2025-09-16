import os
import re
import aiosqlite
from fastapi import HTTPException, status
from providers.database import get_db_path
from models.database import RawQueryRequest

def is_valid_db_name(db_name: str) -> bool:
    """Check if db_name is valid for filesystem and Docker container names."""
    return re.match(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]*$", db_name) is not None

async def db_file_exists(db_name: str) -> bool:
    """Check if the database file exists."""
    db_path = get_db_path(db_name)
    return os.path.exists(db_path)

async def execute_query(db_name: str, query: RawQueryRequest):
    """
    Executes a raw SQL query against the specified database.
    
    This is the most flexible endpoint for data interaction. It allows executing
    SELECT, INSERT, UPDATE, DELETE, and DDL statements. The query can be parameterized
    for safety.
    
    For SELECT queries, the result set is returned in the `data` field.
    For other queries, a success message and the number of rows affected are returned.
    
    Args:
        db_name (str): The name of the target database instance.
        query (RawQueryRequest): The SQL statement and optional parameters.
        
    Returns:
        QueryResponse: The result of the query execution.
        
    Raises:
        HTTPException:
            - 404: If the database `db_name` does not exist.
            - 400: If the SQL statement is invalid or causes an error.
    """
    if not await db_file_exists(db_name):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found.")
    
    db_path = get_db_path(db_name)
    try:
        async with aiosqlite.connect(db_path) as db:
            db.row_factory = aiosqlite.Row
            is_select = query.sql.strip().upper().startswith("SELECT")
            
            params = query.params if query.params is not None else []
            cursor = await db.execute(query.sql, params)
            
            if is_select:
                rows = await cursor.fetchall()
                data = [dict(row) for row in rows]
                return {"data": data, "rows_affected": len(data)}
            else:
                await db.commit()
                return {
                    "message": "Query executed successfully.",
                    "rows_affected": cursor.rowcount
                }
    except aiosqlite.Error as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"SQL Error: {e}")