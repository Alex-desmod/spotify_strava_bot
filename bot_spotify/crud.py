import httpx
import logging

from bot_spotify.database import get_db
from bot_spotify.models import User
from sqlalchemy import select

from web_server.config import SPOTIFY_TOKEN_URL,SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from bot_spotify.config import MAIN_ENDPOINT, get_tops_link


logger = logging.getLogger(__name__)


async def set_user(tg_id, name):
    async for session in get_db():
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id, name=name))
            await session.commit()


async def refresh_access_token(tg_id) -> str|None:
    async for session in get_db():
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user or not user.refresh_token:
            return None

        async with httpx.AsyncClient() as client:
            response = await client.post(SPOTIFY_TOKEN_URL,
                                         data={
                                                "grant_type": "refresh_token",
                                                "refresh_token": user.refresh_token,
                                                "client_id": SPOTIFY_CLIENT_ID,
                                                "client_secret": SPOTIFY_CLIENT_SECRET,
                                                },
                                         headers={"Content-Type": "application/x-www-form-urlencoded"})

        token_data = response.json()

        if "access_token" in token_data:
            user.access_token = token_data["access_token"]
            await session.commit()
            return user.access_token
        else:
            return None


async def get_valid_access_token(tg_id) -> str|None:
    async for session in get_db():
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user or not user.access_token:
            return None

        # Check if the token is working (by test request)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                MAIN_ENDPOINT,
                headers={"Authorization": f"Bearer {user.access_token}"}
                )

        if response.status_code == 200:
            return user.access_token  # The token is valid

        elif response.status_code == 401:
            return await refresh_access_token(tg_id)  # The token is outdated and be refreshed

        return None  # Error


async def get_charts(tg_id, entity, time_range, limit):
    async for session in get_db():
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user or not user.access_token:
            return None

        async with httpx.AsyncClient() as client:
            response = await client.get(
                get_tops_link(entity, time_range, limit),
                headers={"Authorization": f"Bearer {user.access_token}"}
            )

        if response.status_code == 200:
            return response.json()

        return None  # Error


async def get_admins():
    async for session in get_db():
        result = await session.execute(select(User).where(User.is_admin.is_(True)))
        return result.scalars().all()