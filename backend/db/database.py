"""
SQLAlchemy async database connection + session factory.
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

# Convert sync postgres:// URL to async postgresql+asyncpg:// 
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://intellicredit:intellicredit@localhost:5432/intellicredit")
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://").replace("postgres://", "postgresql+asyncpg://")

engine = create_async_engine(ASYNC_DATABASE_URL, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    """Dependency for FastAPI routes."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Create all tables (development) — for production use init.sql via Docker."""
    import asyncpg
    raw_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    try:
        conn = await asyncpg.connect(DATABASE_URL.replace("postgresql://", "") and DATABASE_URL)
        # Read and execute init.sql
        import pathlib
        sql_path = pathlib.Path(__file__).parent / "init.sql"
        if sql_path.exists():
            sql = sql_path.read_text()
            await conn.execute(sql)
        await conn.close()
    except Exception as e:
        print(f"[DB] Could not auto-init schema (may already exist): {e}")
