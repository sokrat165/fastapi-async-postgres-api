import asyncio
from src.core.database import engine
from src.models.chat import Chat

async def reset_chat_table():
    async with engine.begin() as conn:
        print("Dropping Chat table...")
        await conn.run_sync(Chat.__table__.drop)  # يحذف جدول chats
        print("Creating Chat table...")
        await conn.run_sync(Chat.__table__.create)  # ينشئه تاني بالعمود الجديد
    print("Done!")

if __name__ == "__main__":
    asyncio.run(reset_chat_table())
