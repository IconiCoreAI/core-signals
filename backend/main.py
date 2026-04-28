from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import RootModel
import jwt
import os
import asyncpg
from datetime import datetime

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend-hikgyujxe-iconi-core-ai.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Environment Variables
# -----------------------------
SECURE_INTAKE_SECRET = os.getenv("SECURE_INTAKE_SECRET", "default_intake_secret")
JWT_SECRET = os.getenv("JWT_SECRET", "default_jwt_secret")
DATABASE_URL = os.getenv("DATABASE_URL")

# -----------------------------
# Database Connection
# -----------------------------
async def get_db():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL is not set")

    conn = await asyncpg.connect(DATABASE_URL)
    return conn

# Create table on startup
@app.on_event("startup")
async def startup_event():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS intake_events (
            id SERIAL PRIMARY KEY,
            payload JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    await conn.close()

# -----------------------------
# JWT Authentication
# -----------------------------
security = HTTPBearer()

async def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# -----------------------------
# Intake Payload Model (Pydantic v2)
# -----------------------------
class IntakePayload(RootModel[dict]):
    pass

# -----------------------------
# SECURE INTAKE ENDPOINT
# -----------------------------
@app.post("/secure-intake")
async def secure_intake(
    request: Request,
    payload: IntakePayload
):
    # 1. Validate secret via query param
    query_secret = request.query_params.get("secret")

    # 2. Validate secret via header
    header_secret = request.headers.get("X-Secret")

    # 3. Validate via Bearer token
    auth_header = request.headers.get("Authorization")
    bearer_secret = None
    if auth_header and auth_header.startswith("Bearer "):
        bearer_secret = auth_header.split(" ")[1]

    # Check any valid secret
    if query_secret != SECURE_INTAKE_SECRET and \
       header_secret != SECURE_INTAKE_SECRET and \
       bearer_secret != SECURE_INTAKE_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Insert into DB
    conn = await get_db()
    await conn.execute(
        "INSERT INTO intake_events (payload) VALUES ($1)",
        payload.root
    )
    await conn.close()

    return {"status": "ok"}

# -----------------------------
# Protected Route
# -----------------------------
@app.get("/me")
async def me(user=Depends(verify_jwt)):
    return {"status": "authenticated", "user": user}

# -----------------------------
# Health Check
# -----------------------------
@app.get("/")
async def root():
    return {"status": "running"}
