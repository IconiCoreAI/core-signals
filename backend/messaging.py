import os
import asyncpg
import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from cryptography.fernet import Fernet, InvalidToken

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET", "default_jwt_secret")
FERNET_KEY = os.getenv("FERNET_KEY")

router = APIRouter(prefix="/messages", tags=["messages"])
security = HTTPBearer()


def get_fernet() -> Fernet:
    if not FERNET_KEY:
        raise HTTPException(status_code=500, detail="FERNET_KEY is not configured")
    return Fernet(FERNET_KEY.encode() if isinstance(FERNET_KEY, str) else FERNET_KEY)


async def get_db():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL is not set")
    return await asyncpg.connect(DATABASE_URL)


async def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        return jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def create_table():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            channel_type TEXT NOT NULL,
            thread_id TEXT,
            sender_id TEXT NOT NULL,
            recipient_id TEXT,
            body TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    await conn.close()


def _make_thread_id(user_a: str, user_b: str) -> str:
    """Canonical thread ID that's the same regardless of who initiates."""
    return ":".join(sorted([user_a, user_b]))


# -----------------------------
# Request Models
# -----------------------------
class GroupMessageRequest(BaseModel):
    body: str


class PrivateMessageRequest(BaseModel):
    recipient_id: str
    body: str


# -----------------------------
# Group Channel
# -----------------------------
@router.post("/group")
async def send_group_message(
    request: GroupMessageRequest,
    user: dict = Depends(verify_jwt),
):
    sender_id = user.get("sub", "unknown")
    conn = await get_db()
    row = await conn.fetchrow(
        """
        INSERT INTO messages (channel_type, sender_id, body)
        VALUES ('group', $1, $2)
        RETURNING id, channel_type, sender_id, body, created_at
        """,
        sender_id, request.body,
    )
    await conn.close()
    return dict(row)


@router.get("/group")
async def get_group_messages(user: dict = Depends(verify_jwt)):
    conn = await get_db()
    rows = await conn.fetch(
        """
        SELECT id, sender_id, body, created_at
        FROM messages
        WHERE channel_type = 'group'
        ORDER BY created_at ASC
        """
    )
    await conn.close()
    return [dict(r) for r in rows]


# -----------------------------
# Private Messages (Fernet encrypted)
# -----------------------------
@router.post("/private")
async def send_private_message(
    request: PrivateMessageRequest,
    user: dict = Depends(verify_jwt),
):
    sender_id = user.get("sub", "unknown")
    recipient_id = request.recipient_id

    if sender_id == recipient_id:
        raise HTTPException(status_code=400, detail="Cannot send a private message to yourself")

    thread_id = _make_thread_id(sender_id, recipient_id)
    fernet = get_fernet()
    encrypted_body = fernet.encrypt(request.body.encode()).decode()

    conn = await get_db()
    row = await conn.fetchrow(
        """
        INSERT INTO messages (channel_type, thread_id, sender_id, recipient_id, body)
        VALUES ('private', $1, $2, $3, $4)
        RETURNING id, thread_id, sender_id, recipient_id, created_at
        """,
        thread_id, sender_id, recipient_id, encrypted_body,
    )
    await conn.close()
    return dict(row)


@router.get("/private/{thread_id}")
async def get_private_thread(
    thread_id: str,
    user: dict = Depends(verify_jwt),
):
    user_id = user.get("sub", "unknown")

    # Verify the requesting user is one of the two participants in this thread
    participants = set(thread_id.split(":"))
    if user_id not in participants:
        raise HTTPException(status_code=403, detail="Access denied")

    fernet = get_fernet()
    conn = await get_db()
    rows = await conn.fetch(
        """
        SELECT id, sender_id, recipient_id, body, created_at
        FROM messages
        WHERE channel_type = 'private' AND thread_id = $1
        ORDER BY created_at ASC
        """,
        thread_id,
    )
    await conn.close()

    decrypted = []
    for row in rows:
        try:
            body = fernet.decrypt(row["body"].encode()).decode()
        except InvalidToken:
            body = "[unable to decrypt]"
        decrypted.append({
            "id": row["id"],
            "sender_id": row["sender_id"],
            "recipient_id": row["recipient_id"],
            "body": body,
            "created_at": row["created_at"],
        })

    return decrypted
