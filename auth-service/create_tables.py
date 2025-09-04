import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.models import Base

async def create_tables():
    # Используем те же настройки, что и в config.py
    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@auth-db:5432/auth_db"
    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables())