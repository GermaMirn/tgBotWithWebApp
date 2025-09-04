from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Формат: postgresql+asyncpg://user:password@host:port/dbname
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Синхронный движок для CRUD операций
sync_database_url = SQLALCHEMY_DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
engine = create_engine(sync_database_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Асинхронный движок (оставляем для совместимости)
async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

def get_db():
    """Dependency для получения сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
