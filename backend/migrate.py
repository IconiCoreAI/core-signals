import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

async def run_migration():
    url = os.getenv("DATABASE_URL")
    try:
        host_part = url.split('@')[1]
        print(f"Connecting to {host_part}...")
    except Exception:
        print("Connecting to database...")

    conn = await asyncpg.connect(url)
    
    with open('../db/001_notifications_schema.sql', 'r') as f:
        sql = f.read()
        
    print("Executing schema...")
    await conn.execute(sql)
    print("Migration successful.")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migration())
