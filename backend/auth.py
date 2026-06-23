import os
import uuid
import hmac
import asyncio
import smtplib
import asyncpg
import bcrypt
import jwt
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET", "default_jwt_secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_DAYS = 30
ADMIN_RESET_TOKEN = os.getenv("ADMIN_RESET_TOKEN")
CONTACT_GMAIL_USER = os.getenv("CONTACT_GMAIL_USER")
CONTACT_GMAIL_APP_PASSWORD = os.getenv("CONTACT_GMAIL_APP_PASSWORD")
APP_BASE_URL = "https://bali.escapefromrealitytravel.com"

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
    # last_seen: stamped by /auth/signin and /me, read by /admin/travelers
    # (ITS integration). Also in db/migrations/0016_traveler_last_seen.sql.
    await conn.execute(
        "ALTER TABLE travelers ADD COLUMN IF NOT EXISTS last_seen TIMESTAMP;"
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
    conn = await get_db()
    await conn.execute(
        "UPDATE travelers SET last_seen = NOW() WHERE id = $1", row["id"]
    )
    await conn.close()
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


class UpdateNameRequest(BaseModel):
    name: str


@router.patch("/update-name")
async def update_name(req: UpdateNameRequest, user=Depends(verify_jwt)):
    name = req.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name cannot be empty")
    user_id = user.get("sub")
    conn = await get_db()
    row = await conn.fetchrow(
        "UPDATE travelers SET name = $1 WHERE id = $2 RETURNING id, email, name, role",
        name, user_id,
    )
    await conn.close()
    return {"id": row["id"], "email": row["email"], "name": row["name"], "role": row["role"]}


def _send_reset_email(to_email: str, name: str, reset_url: str):
    if not CONTACT_GMAIL_USER or not CONTACT_GMAIL_APP_PASSWORD:
        return
    first_name = name.split()[0] if name else "Traveler"
    body = (
        f"Hi {first_name},\n\n"
        f"You requested a password reset for your Bali Retirement Trip app.\n\n"
        f"Tap the link below to set a new password. It expires in 15 minutes.\n\n"
        f"{reset_url}\n\n"
        f"If you didn't request this, just ignore this email.\n\n"
        f"Safe travels,\n"
        f"Escape From Reality Travel"
    )
    msg = MIMEText(body)
    msg["Subject"] = "Reset your Bali Trip app password"
    msg["From"] = CONTACT_GMAIL_USER
    msg["To"] = to_email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(CONTACT_GMAIL_USER, CONTACT_GMAIL_APP_PASSWORD)
        smtp.send_message(msg)


class ForgotPasswordRequest(BaseModel):
    email: str


@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    email = req.email.lower().strip()
    conn = await get_db()
    row = await conn.fetchrow(
        "SELECT id, email, name, password_hash FROM travelers WHERE email = $1", email
    )
    await conn.close()

    # Always 200 — never reveal whether the email exists
    if not row or not row["password_hash"]:
        return {"status": "ok"}

    payload = {
        "sub": row["id"],
        "fpr": row["password_hash"][-8:],
        "purpose": "pw_reset",
        "exp": datetime.utcnow() + timedelta(minutes=15),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    reset_url = f"{APP_BASE_URL}/?reset={token}"

    try:
        await asyncio.to_thread(_send_reset_email, row["email"], row["name"], reset_url)
    except Exception:
        pass  # email failure must not reveal account existence

    return {"status": "ok"}


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest):
    if len(req.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    try:
        payload = jwt.decode(req.token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Reset link has expired. Please request a new one.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid reset link.")

    if payload.get("purpose") != "pw_reset":
        raise HTTPException(status_code=400, detail="Invalid reset link.")

    user_id = payload.get("sub")
    fpr = payload.get("fpr")

    conn = await get_db()
    row = await conn.fetchrow(
        "SELECT password_hash FROM travelers WHERE id = $1", user_id
    )
    if not row or not row["password_hash"]:
        await conn.close()
        raise HTTPException(status_code=400, detail="Invalid reset link.")

    if row["password_hash"][-8:] != fpr:
        await conn.close()
        raise HTTPException(status_code=400, detail="This reset link has already been used.")

    new_hash = bcrypt.hashpw(req.new_password.encode(), bcrypt.gensalt()).decode()
    await conn.execute(
        "UPDATE travelers SET password_hash = $1 WHERE id = $2", new_hash, user_id
    )
    await conn.close()
    return {"status": "password reset"}


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

