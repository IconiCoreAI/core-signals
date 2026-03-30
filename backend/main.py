import os
import json
import uuid
from typing import List, Optional, Any, Dict
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
import asyncpg
from dotenv import load_dotenv

# Load env variables from root directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.example'))

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/coresignals")

app = FastAPI(title="Core Signals Hub")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Connection Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

# --- Database Setup ---
@app.on_event("startup")
async def startup():
    try:
        app.state.pool = await asyncpg.create_pool(DATABASE_URL)
        print("Connected to PostgreSQL pool successfully.")
    except Exception as e:
        print(f"Warning: Could not connect to database at startup: {e}")
        app.state.pool = None

@app.on_event("shutdown")
async def shutdown():
    if getattr(app.state, "pool", None):
        await app.state.pool.close()

async def get_db():
    if not getattr(app.state, "pool", None):
        raise HTTPException(status_code=503, detail="Database connection pool not available")
    async with app.state.pool.acquire() as connection:
        yield connection

# --- API Models ---
class WebhookPayload(BaseModel):
    source: str
    type: str
    title: str
    body: str
    metadata: Optional[Dict[str, Any]] = None

class NotificationResponse(BaseModel):
    id: uuid.UUID
    source: str
    type: str
    title: str
    body: str
    metadata: Optional[Dict[str, Any]] = None
    read: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Endpoints ---
@app.post("/webhook", response_model=NotificationResponse, status_code=201)
async def receive_webhook(payload: WebhookPayload, db: asyncpg.Connection = Depends(get_db)):
    notification_id = uuid.uuid4()
    
    query = """
    INSERT INTO notifications (id, source, type, title, body, metadata, read)
    VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7)
    RETURNING *;
    """
    
    metadata_json = json.dumps(payload.metadata) if payload.metadata else None
    
    row = await db.fetchrow(
        query,
        notification_id,
        payload.source,
        payload.type,
        payload.title,
        payload.body,
        metadata_json,
        False
    )
    
    if not row:
        raise HTTPException(status_code=500, detail="Failed to save notification")
        
    notification_dict = dict(row)
    if notification_dict.get('metadata') and isinstance(notification_dict['metadata'], str):
        notification_dict['metadata'] = json.loads(notification_dict['metadata'])
        
    # Broadcast to all connected WebSocket clients
    response_obj = NotificationResponse(**notification_dict)
    await manager.broadcast(response_obj.model_dump_json())
    
    return response_obj

@app.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    source: Optional[str] = None,
    type: Optional[str] = None,
    read: Optional[bool] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: asyncpg.Connection = Depends(get_db)
):
    offset = (page - 1) * limit
    
    conditions = []
    params = []
    param_idx = 1
    
    if source is not None:
        conditions.append(f"source = ${param_idx}")
        params.append(source)
        param_idx += 1
        
    if type is not None:
        conditions.append(f"type = ${param_idx}")
        params.append(type)
        param_idx += 1
        
    if read is not None:
        conditions.append(f"read = ${param_idx}")
        params.append(read)
        param_idx += 1
        
    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)
        
    query = f"""
    SELECT * FROM notifications 
    {where_clause} 
    ORDER BY created_at DESC 
    LIMIT ${param_idx} OFFSET ${param_idx + 1};
    """
    
    params.extend([limit, offset])
    
    rows = await db.fetch(query, *params)
    
    results = []
    for row in rows:
        d = dict(row)
        if d.get('metadata') and isinstance(d['metadata'], str):
            d['metadata'] = json.loads(d['metadata'])
        results.append(d)
        
    return results

@app.patch("/notifications/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(notification_id: uuid.UUID, db: asyncpg.Connection = Depends(get_db)):
    query = """
    UPDATE notifications 
    SET read = true 
    WHERE id = $1 
    RETURNING *;
    """
    row = await db.fetchrow(query, notification_id)
    
    if not row:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    d = dict(row)
    if d.get('metadata') and isinstance(d['metadata'], str):
        d['metadata'] = json.loads(d['metadata'])
        
    return d

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection open and accept ping messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
