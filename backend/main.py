from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, Depends, HTTPException, status
from documents import router as documents_router, create_table as create_documents_table
from messaging import router as messaging_router, create_table as create_messages_table
from auth import router as auth_router, create_table as create_auth_table
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import RootModel, BaseModel
import jwt
import os
import asyncpg
import httpx
import asyncio
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

N8N_WEBHOOK_URL = "https://iconicore.app.n8n.cloud/webhook/zWF0zpfo3iwxhp2Y"

async def notify_n8n(payload: dict):
    async with httpx.AsyncClient() as client:
        await client.post(N8N_WEBHOOK_URL, json=payload, timeout=10)

app = FastAPI()
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(messaging_router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://frontend-hikgyujxe-iconi-core-ai.vercel.app",
        "https://frontend-still-petal-6011.fly.dev",
        "https://bali.escapefromrealitytravel.com",
        "http://localhost:5173",
        "http://localhost:4173",
    ],
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
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
SOS_ALERT_EMAIL = "8038145792@vtext.com"

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
    await create_auth_table()
    await create_documents_table()
    await create_messages_table()

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

    await notify_n8n(payload.root)

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

class SOSRequest(BaseModel):
    name: str = ""
    level: str = "HIGH"


def _send_sos_email(name: str, level: str, timestamp: str):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        return
    body = (
        f"BALI SOS ALERT\n\n"
        f"Traveler: {name}\n"
        f"Level: {level}\n"
        f"Time: {timestamp} UTC\n\n"
        f"Immediate assistance required."
    )
    msg = MIMEText(body)
    msg["Subject"] = "🚨 BALI SOS ALERT"
    msg["From"] = GMAIL_USER
    msg["To"] = SOS_ALERT_EMAIL
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        smtp.send_message(msg)


@app.post("/sos")
async def sos(request: SOSRequest, user=Depends(verify_jwt)):
    user_email = user.get("email", user.get("sub", "unknown"))
    name = request.name or user_email
    timestamp = datetime.utcnow().isoformat()

    payload = {
        "type": "sos",
        "user_id": user.get("sub"),
        "user_email": user_email,
        "name": name,
        "level": request.level,
        "timestamp": timestamp,
    }
    await notify_n8n(payload)
    conn = await get_db()
    await conn.execute("INSERT INTO intake_events (payload) VALUES ($1)", payload)
    await conn.close()

    try:
        await asyncio.to_thread(_send_sos_email, name, request.level, timestamp)
    except Exception:
        pass  # email failure must never block an SOS response

    return {"status": "sent"}


@app.get("/health")
async def health():
    try:
        conn = await get_db()
        await conn.fetchval("SELECT 1")
        await conn.close()
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")
