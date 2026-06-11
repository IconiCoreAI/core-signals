"""Service surface for ITS (Iconic Travel System): /admin/* endpoints.

Machine-to-machine only: every endpoint requires the X-ITS-Key header to
match BALI_API_KEY (constant-time compare). No traveler JWTs here, and the
traveler-facing endpoints are untouched. Messages sent through this surface
carry sender_id 'concierge', which is how they appear in the app chat.
"""
import os
import secrets
import uuid

import asyncpg
from cryptography.fernet import Fernet
from fastapi import APIRouter, File, Form, Header, HTTPException, UploadFile
from pydantic import BaseModel

from r2 import upload_file

DATABASE_URL = os.getenv("DATABASE_URL")
FERNET_KEY = os.getenv("FERNET_KEY")

SENDER_ID = "concierge"

router = APIRouter(prefix="/admin", tags=["its-integration"])


async def get_db():
    return await asyncpg.connect(DATABASE_URL)


def verify_its_key(x_its_key: str = Header(None)):
    expected = os.getenv("BALI_API_KEY")
    if not expected:
        raise HTTPException(status_code=503, detail="ITS integration is not configured")
    if not (x_its_key and secrets.compare_digest(x_its_key, expected)):
        raise HTTPException(status_code=401, detail="Invalid ITS key")


class GroupMessageIn(BaseModel):
    body: str


class PrivateMessageIn(BaseModel):
    recipient_id: str
    body: str


def _make_thread_id(user_a: str, user_b: str) -> str:
    return ":".join(sorted([user_a, user_b]))


@router.get("/travelers")
async def list_travelers(x_its_key: str = Header(None)):
    verify_its_key(x_its_key)
    conn = await get_db()
    rows = await conn.fetch(
        """
        SELECT id, name, email,
               password_hash IS NOT NULL AS registered,
               created_at AS signup_date,
               last_seen
        FROM travelers
        WHERE role != 'admin'
        ORDER BY name NULLS LAST, email
        """
    )
    await conn.close()
    return [dict(r) for r in rows]


@router.post("/messages/group")
async def send_group_message(request: GroupMessageIn, x_its_key: str = Header(None)):
    verify_its_key(x_its_key)
    conn = await get_db()
    row = await conn.fetchrow(
        """
        INSERT INTO messages (channel_type, sender_id, body)
        VALUES ('group', $1, $2)
        RETURNING id, channel_type, sender_id, body, created_at
        """,
        SENDER_ID, request.body,
    )
    await conn.close()
    return dict(row)


@router.post("/messages/private")
async def send_private_message(request: PrivateMessageIn, x_its_key: str = Header(None)):
    verify_its_key(x_its_key)
    if not FERNET_KEY:
        raise HTTPException(status_code=500, detail="FERNET_KEY is not configured")
    thread_id = _make_thread_id(SENDER_ID, request.recipient_id)
    encrypted = Fernet(
        FERNET_KEY.encode() if isinstance(FERNET_KEY, str) else FERNET_KEY
    ).encrypt(request.body.encode()).decode()

    conn = await get_db()
    row = await conn.fetchrow(
        """
        INSERT INTO messages (channel_type, thread_id, sender_id, recipient_id, body)
        VALUES ('private', $1, $2, $3, $4)
        RETURNING id, thread_id, sender_id, recipient_id, created_at
        """,
        thread_id, SENDER_ID, request.recipient_id, encrypted,
    )
    await conn.close()
    return dict(row)


@router.post("/documents")
async def upload_document(
    file: UploadFile = File(...),
    target: str = Form(...),  # 'all' or a traveler id
    x_its_key: str = Header(None),
):
    verify_its_key(x_its_key)
    if target == "all":
        key = f"documents/trip/{uuid.uuid4()}_{file.filename}"
        visible_to_all, uploaded_by, doc_type = True, SENDER_ID, "trip_doc"
    else:
        conn = await get_db()
        traveler = await conn.fetchrow(
            "SELECT id FROM travelers WHERE id = $1", target
        )
        await conn.close()
        if traveler is None:
            raise HTTPException(status_code=404, detail="No such traveler")
        key = f"documents/personal/{target}/{uuid.uuid4()}_{file.filename}"
        visible_to_all, uploaded_by, doc_type = False, target, "other"

    upload_file(file.file, key, file.content_type or "application/octet-stream")

    conn = await get_db()
    row = await conn.fetchrow(
        """
        INSERT INTO documents (key, filename, document_type, uploaded_by,
                               visible_to_all, admin_access_granted)
        VALUES ($1, $2, $3, $4, $5, TRUE)
        RETURNING id, filename, document_type, visible_to_all, uploaded_by, created_at
        """,
        key, file.filename, doc_type, uploaded_by, visible_to_all,
    )
    await conn.close()
    return dict(row)
