import os
import uuid
import asyncpg
import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET", "default_jwt_secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_DAYS = 30

router = APIRouter(prefix="/auth", tags=["auth"])


async def get_db():
    return await asyncpg.connect(DATABASE_URL)


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
