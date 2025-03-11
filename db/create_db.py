import aiosqlite
import asyncio


DB_PATH = "./db/database.db"


async def create_table():
    async with aiosqlite.connect(DB_PATH) as db:
        # Создание таблицы users
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                firstname TEXT NOT NULL,
                middlename TEXT,
                lastname TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')

        await db.commit()


async def main():
    await create_table()


if __name__ == '__main__':
    asyncio.run(main())