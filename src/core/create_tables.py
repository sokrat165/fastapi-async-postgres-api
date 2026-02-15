# src/core/create_tables.py
import asyncio
from src.core.database import Base, db_factory

async def reset_tables():
    # اختار أي database هنا، مثلاً "local"
    engine = db_factory.engines["local"]

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    print("Tables reset completed")

if __name__ == "__main__":
    asyncio.run(reset_tables())
