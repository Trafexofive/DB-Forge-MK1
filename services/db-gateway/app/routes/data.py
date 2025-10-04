from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Optional, Dict, Any, List
from auth.auth import verify_api_key_header
from services.database import execute_query, db_file_exists, is_valid_db_name
from models.database import (
    RawQueryRequest, QueryResponse, CreateTableRequest, CreateTableResponse,
    InsertRequest, InsertResponse, ColumnDefinition
)
from providers.database import get_db_path
import aiosqlite
import urllib.parse

router = APIRouter(
    prefix="/api/db",
    tags=["data"],
    dependencies=[Depends(verify_api_key_header)]
)

@router.post("/{db_name}/query", response_model=QueryResponse)
async def execute_raw_query(db_name: str, query: RawQueryRequest):
    """
    Execute a raw SQL query against a specific database.
    
    This endpoint allows execution of any valid SQL statement including:
    - SELECT queries (returns data)
    - INSERT, UPDATE, DELETE queries (returns rows_affected)
    - DDL statements like CREATE TABLE, ALTER TABLE, etc.
    
    The query can be parameterized using the params array to prevent SQL injection.
    
    Args:
        db_name (str): The name of the target database instance
        query (RawQueryRequest): The SQL statement and optional parameters
        
    Returns:
        QueryResponse: Query results or execution status
        
    Raises:
        HTTPException:
            - 400: Invalid database name or SQL error
            - 404: Database not found
    """
    if not is_valid_db_name(db_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid database name.")
    
    return await execute_query(db_name, query)

@router.post("/{db_name}/tables", response_model=CreateTableResponse, status_code=status.HTTP_201_CREATED)
async def create_table(db_name: str, request: CreateTableRequest):
    """
    Create a new table in the specified database.
    
    This endpoint provides a structured way to create tables with proper column
    definitions, constraints, and types. It's more user-friendly than raw SQL
    for basic table creation.
    
    Args:
        db_name (str): The name of the target database instance
        request (CreateTableRequest): Table name and column definitions
        
    Returns:
        CreateTableResponse: Success message confirming table creation
        
    Raises:
        HTTPException:
            - 400: Invalid database name, table name, or SQL error
            - 404: Database not found
    """
    if not is_valid_db_name(db_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid database name.")
    
    if not await db_file_exists(db_name):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found.")
    
    # Build CREATE TABLE SQL statement
    table_name = request.table_name
    column_definitions = []
    
    for col in request.columns:
        col_def = f"{col.name} {col.type}"
        if col.primary_key:
            col_def += " PRIMARY KEY"
        if col.not_null:
            col_def += " NOT NULL"
        if col.default is not None:
            col_def += f" DEFAULT {col.default}"
        column_definitions.append(col_def)
    
    sql = f"CREATE TABLE {table_name} ({', '.join(column_definitions)})"
    
    # Execute the CREATE TABLE statement
    query_request = RawQueryRequest(sql=sql)
    await execute_query(db_name, query_request)
    
    return CreateTableResponse(message=f"Table '{table_name}' created successfully.")

@router.post("/{db_name}/tables/{table_name}/rows", response_model=InsertResponse, status_code=status.HTTP_201_CREATED)
async def insert_rows(db_name: str, table_name: str, request: InsertRequest):
    """
    Insert multiple rows into a specific table.
    
    This endpoint provides a structured way to insert data into tables without
    writing raw SQL. All rows in the request will be inserted in a single transaction.
    
    Args:
        db_name (str): The name of the target database instance
        table_name (str): The name of the target table
        request (InsertRequest): List of rows to insert (as dictionaries)
        
    Returns:
        InsertResponse: Success message and number of rows inserted
        
    Raises:
        HTTPException:
            - 400: Invalid database name, SQL error, or malformed data
            - 404: Database not found
    """
    if not is_valid_db_name(db_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid database name.")
    
    if not await db_file_exists(db_name):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found.")
    
    if not request.rows:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No rows provided for insertion.")
    
    # Get column names from the first row
    columns = list(request.rows[0].keys())
    placeholders = ", ".join(["?" for _ in columns])
    column_names = ", ".join(columns)
    
    sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
    
    db_path = get_db_path(db_name)
    try:
        async with aiosqlite.connect(db_path) as db:
            total_inserted = 0
            for row in request.rows:
                # Ensure all rows have the same columns
                if set(row.keys()) != set(columns):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="All rows must have the same columns."
                    )
                
                values = [row[col] for col in columns]
                cursor = await db.execute(sql, values)
                total_inserted += cursor.rowcount
            
            await db.commit()
            
            return InsertResponse(
                message="Rows inserted successfully.",
                rows_affected=total_inserted
            )
    except aiosqlite.Error as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"SQL Error: {e}")

@router.get("/{db_name}/tables/{table_name}/rows", response_model=QueryResponse)
async def get_rows(
    db_name: str, 
    table_name: str,
    limit: Optional[int] = Query(None, description="Maximum number of rows to return"),
    offset: Optional[int] = Query(0, description="Number of rows to skip"),
    **query_params: str
):
    """
    Retrieve rows from a specific table with optional filtering.
    
    This endpoint provides a structured way to query table data with optional
    filtering via query parameters. Each query parameter becomes a WHERE condition
    using exact matching (column_name = value).
    
    Args:
        db_name (str): The name of the target database instance
        table_name (str): The name of the target table
        limit (int, optional): Maximum number of rows to return
        offset (int, optional): Number of rows to skip (for pagination)
        **query_params: Additional query parameters for filtering (e.g., ?age=25&status=active)
        
    Returns:
        QueryResponse: Retrieved rows and count
        
    Raises:
        HTTPException:
            - 400: Invalid database name or SQL error
            - 404: Database not found
    """
    if not is_valid_db_name(db_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid database name.")
    
    if not await db_file_exists(db_name):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found.")
    
    # Build SELECT query with optional WHERE clause
    sql = f"SELECT * FROM {table_name}"
    params = []
    
    # Add WHERE conditions from query parameters
    # Remove FastAPI internal parameters
    filtered_params = {k: v for k, v in query_params.items() 
                      if k not in ['limit', 'offset']}
    
    if filtered_params:
        where_conditions = []
        for key, value in filtered_params.items():
            where_conditions.append(f"{key} = ?")
            params.append(value)
        sql += f" WHERE {' AND '.join(where_conditions)}"
    
    # Add LIMIT and OFFSET
    if limit is not None:
        sql += f" LIMIT {limit}"
        if offset:
            sql += f" OFFSET {offset}"
    
    query_request = RawQueryRequest(sql=sql, params=params)
    return await execute_query(db_name, query_request)