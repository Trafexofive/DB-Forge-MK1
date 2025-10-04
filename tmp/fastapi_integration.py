from fastapi import FastAPI, HTTPException
from ..clients.python.dbforge_client.client import DBForgeClient, DatabaseNotFound

app = FastAPI()
dbforge = DBForgeClient()

@app.on_event("startup")
async def startup():
    # Initialize application database
    db = dbforge.get_database("medical_knowledge_db")
    
    # Setup schema
    db.create_table("users", [
        {"name": "id", "type": "INTEGER", "primary_key": True},
        {"name": "email", "type": "TEXT", "not_null": True, "unique": True},
        {"name": "created_at", "type": "DATETIME", "default": "CURRENT_TIMESTAMP"}
    ])

@app.post("/users")
async def create_user(email: str):
    try:
        db = dbforge.get_database("app_main")
        result = db.insert_rows("users", [{"email": email}])
        return {"success": True, "rows_affected": result["rows_affected"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users")
async def get_users():
    db = dbforge.get_database("app_main")
    return db.select_rows("users")
