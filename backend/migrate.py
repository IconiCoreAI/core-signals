import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

SCHEMA = """
-- Traveler accounts (id maps to JWT 'sub' claim)
CREATE TABLE IF NOT EXISTS travelers (
    id            TEXT PRIMARY KEY,
    email         TEXT UNIQUE NOT NULL,
    name          TEXT,
    role          TEXT NOT NULL DEFAULT 'traveler',
    password_hash TEXT,
    created_at    TIMESTAMP DEFAULT NOW()
);

-- Named group channels
CREATE TABLE IF NOT EXISTS channels (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    slug        TEXT UNIQUE NOT NULL,
    created_by  TEXT REFERENCES travelers(id),
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Channel membership
CREATE TABLE IF NOT EXISTS channel_members (
    id          SERIAL PRIMARY KEY,
    channel_id  INTEGER NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    traveler_id TEXT NOT NULL REFERENCES travelers(id) ON DELETE CASCADE,
    joined_at   TIMESTAMP DEFAULT NOW(),
    UNIQUE (channel_id, traveler_id)
);

-- Channel messages
CREATE TABLE IF NOT EXISTS messages (
    id          SERIAL PRIMARY KEY,
    channel_id  INTEGER NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    sender_id   TEXT NOT NULL REFERENCES travelers(id),
    body        TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Private 1:1 threads (id is canonical "userA:userB" sorted)
CREATE TABLE IF NOT EXISTS private_threads (
    id            TEXT PRIMARY KEY,
    participant_a TEXT NOT NULL REFERENCES travelers(id),
    participant_b TEXT NOT NULL REFERENCES travelers(id),
    created_at    TIMESTAMP DEFAULT NOW()
);

-- Private messages (Fernet-encrypted body)
CREATE TABLE IF NOT EXISTS private_messages (
    id          SERIAL PRIMARY KEY,
    thread_id   TEXT NOT NULL REFERENCES private_threads(id) ON DELETE CASCADE,
    sender_id   TEXT NOT NULL REFERENCES travelers(id),
    body        TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Document metadata (file stored in R2)
CREATE TABLE IF NOT EXISTS documents (
    id                   SERIAL PRIMARY KEY,
    key                  TEXT NOT NULL,
    filename             TEXT NOT NULL,
    document_type        TEXT NOT NULL,
    uploaded_by          TEXT NOT NULL,
    visible_to_all       BOOLEAN NOT NULL DEFAULT FALSE,
    admin_access_granted BOOLEAN NOT NULL DEFAULT TRUE,
    created_at           TIMESTAMP DEFAULT NOW()
);

-- Triage log for intake events routed via n8n
CREATE TABLE IF NOT EXISTS triage_log (
    id          SERIAL PRIMARY KEY,
    payload     JSONB NOT NULL,
    source      TEXT NOT NULL DEFAULT 'secure-intake',
    status      TEXT NOT NULL DEFAULT 'new',
    reviewed_by TEXT REFERENCES travelers(id),
    created_at  TIMESTAMP DEFAULT NOW()
);
"""

async def migrate():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set in .env")

    try:
        host = url.split("@")[1]
        print(f"Connecting to {host}...")
    except Exception:
        print("Connecting to database...")

    conn = await asyncpg.connect(url)
    try:
        await conn.execute(SCHEMA)
        print("Migration complete. Tables created (or already existed):")
        rows = await conn.fetch(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
        )
        for row in rows:
            print(f"  - {row['tablename']}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(migrate())
