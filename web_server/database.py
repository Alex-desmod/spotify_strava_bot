from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os

SPOTIFY_DB_PATH = os.path.abspath("../shared/db/spotify.db")
STRAVA_DB_PATH = os.path.abspath("../shared/db/strava.db")

spotify_engine = create_async_engine(f"sqlite+aiosqlite:///{SPOTIFY_DB_PATH}")
strava_engine = create_async_engine(f"sqlite+aiosqlite:///{STRAVA_DB_PATH}")

# Making sessions
SpotifySessionLocal = sessionmaker(spotify_engine, class_=AsyncSession, expire_on_commit=False)
StravaSessionLocal = sessionmaker(strava_engine, class_=AsyncSession, expire_on_commit=False)

async def get_spotify_session():
    async with SpotifySessionLocal() as session:
        yield session

async def get_strava_session():
    async with StravaSessionLocal() as session:
        yield session
