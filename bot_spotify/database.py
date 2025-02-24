from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os

DB_PATH = os.path.abspath("../shared/db/spotify.db")

# Async engine for SQLite
engine = create_async_engine(f"sqlite+aiosqlite:///{DB_PATH}")

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Function for getting DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
