"""
One-shot script: uploads Bali trip documents to R2 and registers them
in the Neon documents table as visible_to_all trip docs.

Run from backend/:
    source venv/bin/activate
    python upload_trip_docs.py
"""

import asyncio
import os
import uuid
import sys
from pathlib import Path
import asyncpg
import boto3
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_ENDPOINT = os.getenv("R2_ENDPOINT", f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com")

DOCS = [
    {
        "path": Path("/Users/monetplanter/Downloads/Pam Retirement Bali 2026 Travel Guide .pdf"),
        "document_type": "trip_doc",
        "content_type": "application/pdf",
    },
    {
        "path": Path("/Users/monetplanter/Downloads/Bali 2026 MASTER OPERATIONS sheet.pdf"),
        "document_type": "trip_doc",
        "content_type": "application/pdf",
    },
]


def get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


def upload_to_r2(file_path: Path, content_type: str) -> str:
    key = f"documents/trip/{uuid.uuid4()}_{file_path.name}"
    client = get_r2_client()
    with open(file_path, "rb") as f:
        client.upload_fileobj(f, R2_BUCKET_NAME, key, ExtraArgs={"ContentType": content_type})
    return key


async def get_admin_id(conn) -> str:
    row = await conn.fetchrow("SELECT id FROM travelers WHERE role = 'admin' LIMIT 1")
    return row["id"] if row else "admin_script"


async def register_in_db(conn, key: str, filename: str, document_type: str, uploaded_by: str) -> int:
    row = await conn.fetchrow(
        """
        INSERT INTO documents (key, filename, document_type, uploaded_by, visible_to_all, admin_access_granted)
        VALUES ($1, $2, $3, $4, TRUE, TRUE)
        RETURNING id
        """,
        key, filename, document_type, uploaded_by,
    )
    return row["id"]


async def main():
    missing = [d["path"] for d in DOCS if not d["path"].exists()]
    if missing:
        print("ERROR: File(s) not found:")
        for p in missing:
            print(f"  {p}")
        sys.exit(1)

    conn = await asyncpg.connect(DATABASE_URL)
    try:
        uploaded_by = await get_admin_id(conn)
        print(f"Uploading as: {uploaded_by}\n")

        for doc in DOCS:
            path: Path = doc["path"]
            print(f"Uploading  {path.name} ...")
            key = upload_to_r2(path, doc["content_type"])
            doc_id = await register_in_db(conn, key, path.name, doc["document_type"], uploaded_by)
            print(f"  R2 key : {key}")
            print(f"  DB id  : {doc_id}")
            print()

        print("Done. Both documents are registered and visible to all 9 travelers.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
