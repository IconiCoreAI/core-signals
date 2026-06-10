import os
import uuid
import hmac
import asyncpg
import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET", "default_jwt_secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_DAYS = 30
ADMIN_RESET_TOKEN = os.getenv("ADMIN_RESET_TOKEN")

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


async def get_db():
    return await asyncpg.connect(DATABASE_URL)


async def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        return jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def create_table():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS travelers (
            id            TEXT PRIMARY KEY,
            email         TEXT UNIQUE NOT NULL,
            name          TEXT,
            role          TEXT NOT NULL DEFAULT 'traveler',
            password_hash TEXT,
            created_at    TIMESTAMP DEFAULT NOW()
        );
    """)
    # Add column to existing tables that predate this field
    await conn.execute(
        "ALTER TABLE travelers ADD COLUMN IF NOT EXISTS password_hash TEXT;"
    )
    await conn.close()


def _make_token(user_id: str, email: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRY_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


class SignupRequest(BaseModel):
    email: str
    password: str
    name: str = ""


class SigninRequest(BaseModel):
    email: str
    password: str


@router.post("/signup")
async def signup(req: SignupRequest):
    password_hash = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode()
    user_id = str(uuid.uuid4())
    conn = await get_db()
    try:
        row = await conn.fetchrow(
            """
            INSERT INTO travelers (id, email, name, password_hash)
            VALUES ($1, $2, $3, $4)
            RETURNING id, email, name, role
            """,
            user_id, req.email.lower().strip(), req.name.strip(), password_hash,
        )
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=409, detail="Email already registered")
    finally:
        await conn.close()
    token = _make_token(row["id"], row["email"], row["role"])
    return {
        "token": token,
        "user": {"id": row["id"], "email": row["email"], "name": row["name"], "role": row["role"]},
    }


@router.post("/signin")
async def signin(req: SigninRequest):
    conn = await get_db()
    row = await conn.fetchrow(
        "SELECT id, email, name, role, password_hash FROM travelers WHERE email = $1",
        req.email.lower().strip(),
    )
    await conn.close()
    if not row or not row["password_hash"]:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not bcrypt.checkpw(req.password.encode(), row["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = _make_token(row["id"], row["email"], row["role"])
    return {
        "token": token,
        "user": {"id": row["id"], "email": row["email"], "name": row["name"], "role": row["role"]},
    }


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/change-password")
async def change_password(req: ChangePasswordRequest, user=Depends(verify_jwt)):
    if len(req.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")
    user_id = user.get("sub")
    conn = await get_db()
    row = await conn.fetchrow(
        "SELECT password_hash FROM travelers WHERE id = $1", user_id
    )
    if not row or not row["password_hash"]:
        await conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    if not bcrypt.checkpw(req.current_password.encode(), row["password_hash"].encode()):
        await conn.close()
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    new_hash = bcrypt.hashpw(req.new_password.encode(), bcrypt.gensalt()).decode()
    await conn.execute(
        "UPDATE travelers SET password_hash = $1 WHERE id = $2", new_hash, user_id
    )
    await conn.close()
    return {"status": "password updated"}


class AdminResetRequest(BaseModel):
    email: str
    new_password: str


@router.post("/admin-reset")
async def admin_reset(req: AdminResetRequest, x_admin_token: str = Header(None)):
    # Guarded by a shared secret (ADMIN_RESET_TOKEN), not a JWT — Monet runs this
    # via curl to reset a locked-out traveler. No frontend.
    if not ADMIN_RESET_TOKEN:
        raise HTTPException(status_code=503, detail="Admin reset is not configured")
    if not x_admin_token or not hmac.compare_digest(x_admin_token, ADMIN_RESET_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid admin token")
    if len(req.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")

    new_hash = bcrypt.hashpw(req.new_password.encode(), bcrypt.gensalt()).decode()
    email = req.email.lower().strip()
    conn = await get_db()
    status = await conn.execute(
        "UPDATE travelers SET password_hash = $1 WHERE email = $2", new_hash, email
    )
    await conn.close()
    if int(status.split()[-1]) == 0:
        raise HTTPException(status_code=404, detail="Traveler not found")
    return {"status": "password reset", "email": email}

