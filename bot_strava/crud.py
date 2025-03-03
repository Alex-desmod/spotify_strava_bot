import httpx
import logging

from datetime import datetime

from bot_strava.config import STRAVA_CLIENT_SECRET, STRAVA_CLIENT_ID, get_activity_link
from bot_strava.database import get_db
from bot_strava.models import User
from sqlalchemy import select

from web_server.config import STRAVA_TOKEN_URL


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
            response = await client.post(STRAVA_TOKEN_URL,
                                         data={
                                                "grant_type": "refresh_token",
                                                "refresh_token": user.refresh_token,
                                                "client_id": STRAVA_CLIENT_ID,
                                                "client_secret": STRAVA_CLIENT_SECRET,
                                                })

        token_data = response.json()

        if "access_token" in token_data:
            user.access_token = token_data["access_token"]
            user.refresh_token = token_data["refresh_token"]
            user.expires_at = token_data["expires_at"]
            await session.commit()
            return user.access_token
        else:
            return None


async def get_valid_access_token(tg_id) -> str|None:
    async for session in get_db():
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user or not user.access_token:
            return None

    current_epoch = int(datetime.now().timestamp())
    if user.expires_at < current_epoch:
        return await refresh_access_token(tg_id)  # The token is outdated and must be refreshed
    else:
        return user.access_token    # The token is valid


async def get_activities(tg_id, before, after, page=1):
    async for session in get_db():
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user or not user.access_token:
            return None

    async with httpx.AsyncClient() as client:
        response = await client.get(
            get_activity_link(before, after, page),
            headers={"Authorization": f"Bearer {user.access_token}"}
        )

    if response.status_code == 200:
        return response.json()

    return None  # Error


async def get_admins():
    async for session in get_db():
        result = await session.execute(select(User).where(User.is_admin.is_(True)))
        return result.scalars().all()

