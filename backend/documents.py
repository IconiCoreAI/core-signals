import uuid
import os
import asyncpg
import jwt
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Literal

from r2 import upload_file, generate_presigned_url, delete_file as r2_delete

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET", "default_jwt_secret")

DocumentType = Literal["passport", "insurance", "trip_doc", "other"]

router = APIRouter(prefix="/documents", tags=["documents"])
security = HTTPBearer()


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
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            key TEXT NOT NULL,
            filename TEXT NOT NULL,
            document_type TEXT NOT NULL,
            uploaded_by TEXT NOT NULL,
            visible_to_all BOOLEAN NOT NULL DEFAULT FALSE,
            admin_access_granted BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    await conn.close()


@router.get("")
async def list_documents(user: dict = Depends(verify_jwt)):
    user_id = user.get("sub", "unknown")
    is_admin = user.get("role") == "admin"
    conn = await get_db()
    if is_admin:
        rows = await conn.fetch(
            "SELECT id, filename, document_type, visible_to_all, uploaded_by, created_at FROM documents ORDER BY created_at DESC"
        )
    else:
        rows = await conn.fetch(
            """
            SELECT id, filename, document_type, visible_to_all, uploaded_by, created_at
            FROM documents
            WHERE visible_to_all = TRUE OR uploaded_by = $1
            ORDER BY created_at DESC
            """,
            user_id,
        )
    await conn.close()
    return [dict(r) for r in rows]


def _require_admin(user: dict):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")


@router.post("/trip")
async def upload_trip_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Form("trip_doc"),
    user: dict = Depends(verify_jwt),
):
    _require_admin(user)
    user_id = user.get("sub", "unknown")
    key = f"documents/trip/{uuid.uuid4()}_{file.filename}"
    upload_file(file.file, key, file.content_type or "application/octet-stream")

    conn = await get_db()
    row = await conn.fetchrow(
        """
        INSERT INTO documents (key, filename, document_type, uploaded_by, visible_to_all, admin_access_granted)
        VALUES ($1, $2, $3, $4, TRUE, TRUE)
        RETURNING id, filename, document_type, visible_to_all, created_at
        """,
        key, file.filename, document_type, user_id,
    )
    await conn.close()
    return dict(row)


@router.post("/personal")
async def upload_personal_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Form("other"),
    user: dict = Depends(verify_jwt),
):
    user_id = user.get("sub", "unknown")
    key = f"documents/personal/{user_id}/{uuid.uuid4()}_{file.filename}"
    upload_file(file.file, key, file.content_type or "application/octet-stream")

    # Passport defaults to admin_access_granted=False
    admin_access = document_type != "passport"

    conn = await get_db()
    row = await conn.fetchrow(
        """
        INSERT INTO documents (key, filename, document_type, uploaded_by, visible_to_all, admin_access_granted)
        VALUES ($1, $2, $3, $4, FALSE, $5)
        RETURNING id, filename, document_type, visible_to_all, admin_access_granted, uploaded_by, created_at
        """,
        key, file.filename, document_type, user_id, admin_access,
    )
    await conn.close()
    return dict(row)


@router.get("/{document_id}/download")
async def get_download_link(
    document_id: int,
    user: dict = Depends(verify_jwt),
):
    user_id = user.get("sub", "unknown")
    is_admin = user.get("role") == "admin"

    conn = await get_db()
    doc = await conn.fetchrow("SELECT * FROM documents WHERE id = $1", document_id)
    await conn.close()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    is_owner = doc["uploaded_by"] == user_id
    can_access = is_admin or is_owner or doc["visible_to_all"]

    if not can_access:
        raise HTTPException(status_code=403, detail="Access denied")

    url = generate_presigned_url(doc["key"], expires_in=3600)
    return {"url": url, "expires_in": 3600}


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    user: dict = Depends(verify_jwt),
):
    user_id = user.get("sub", "unknown")
    is_admin = user.get("role") == "admin"

    conn = await get_db()
    doc = await conn.fetchrow("SELECT * FROM documents WHERE id = $1", document_id)

    if not doc:
        await conn.close()
        raise HTTPException(status_code=404, detail="Document not found")

    if not is_admin and doc["uploaded_by"] != user_id:
        await conn.close()
        raise HTTPException(status_code=403, detail="You can only delete your own documents")

    await conn.execute("DELETE FROM documents WHERE id = $1", document_id)
    await conn.close()

    r2_delete(doc["key"])
    return {"status": "deleted", "id": document_id}
