import asyncpg
from config import DATABASE_URL

_pool = None

async def get_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL)
    return _pool

async def init_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS raffles (
                id SERIAL PRIMARY KEY,
                max_participants INTEGER,
                payment_url TEXT,
                current_participants INTEGER DEFAULT 0,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS participants (
                id SERIAL PRIMARY KEY,
                username TEXT,
                raffle_id INTEGER,
                paid BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

async def create_raffle(max_participants, payment_url):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO raffles (max_participants, payment_url) VALUES ($1, $2) RETURNING id",
            max_participants, payment_url
        )
        return row['id']

async def add_participant(username, raffle_id):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO participants (username, raffle_id, paid) VALUES ($1, $2, $3)",
            username, raffle_id, False
        )
        await conn.execute(
            "UPDATE raffles SET current_participants = current_participants + 1 WHERE id = $1",
            raffle_id
        )

async def get_raffle(raffle_id):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM raffles WHERE id = $1",
            raffle_id
        )
        return row

async def mark_paid(username, raffle_id):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE participants SET paid = TRUE WHERE username = $1 AND raffle_id = $2",
            username, raffle_id
        )

async def get_paid_participants(raffle_id):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT username FROM participants WHERE raffle_id = $1 AND paid = TRUE",
            raffle_id
        )
        return [row['username'] for row in rows]
