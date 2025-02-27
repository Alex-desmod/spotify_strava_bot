from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os

from bot_strava.models import Base

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "shared", "db", "strava.db")

# Async engine for SQLite
engine = create_async_engine(url=f"sqlite+aiosqlite:///{DB_PATH}")

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Function for DB initialization
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Function for getting DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
