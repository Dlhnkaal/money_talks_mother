import asyncio
import asyncpg
from config import DATABASE_URL

async def run_migration():
    conn = await asyncpg.connect(DATABASE_URL)
    with open("initial.sql", "r", encoding="utf-8") as f:
        sql = f.read()
    await conn.execute(sql)
    await conn.close()
    print("✅ Migration completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_migration())
