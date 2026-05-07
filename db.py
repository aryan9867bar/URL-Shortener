from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import settings
from models import Base
import asyncio

DATABASE_URL = settings.DATABASE_URL

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

# Session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency (used in FastAPI routes)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# TEST CONNECTION
async def test_connection():
    try:
        async with engine.connect() as conn:
            print("✅ Connected to DB")
    except Exception as e:
        print("❌ DB connection failed:", e)


# CREATE TABLES
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created successfully")


# MAIN ENTRY (single event loop)
async def main():
    await test_connection()
    await create_tables()


if __name__ == "__main__":
    asyncio.run(main())