import aiosqlite

DB_PATH = "bot.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS raffles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                max_participants INTEGER,
                ticket_price INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                raffle_id INTEGER,
                paid BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def add_participant(username, raffle_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO participants (username, raffle_id, paid) VALUES (?, ?, ?)",
            (username, raffle_id, False)
        )
        await db.commit()

async def get_participant_count(raffle_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM participants WHERE raffle_id = ? AND paid = 1",
            (raffle_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def mark_paid(username, raffle_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE participants SET paid = 1 WHERE username = ? AND raffle_id = ?",
            (username, raffle_id)
        )
        await db.commit()

async def get_paid_participants(raffle_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT username FROM participants WHERE raffle_id = ? AND paid = 1",
            (raffle_id,)
        ) as cursor:
            return [row[0] for row in await cursor.fetchall()]
