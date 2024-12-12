#!/usr/bin/env python3
import asyncio
import aiosqlite

DATABASE = "users.db"

async def async_fetch_users():
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute("SELECT * FROM users;")
        results = await cursor.fetchall()
        await cursor.close()
        return results

async def async_fetch_older_users():
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute("SELECT * FROM users WHERE age > 40;")
        results = await cursor.fetchall()
        await cursor.close()
        return results

async def fetch_concurrently():
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )

    print("All Users:")
    for row in all_users:
        print(row)

    print("\nUsers Older Than 40:")
    for row in older_users:
        print(row)

if __name__ == "__main__":
    asyncio.run(fetch_concurrently())
