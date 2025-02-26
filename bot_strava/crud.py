import httpx
import logging

from bot_strava.database import get_db
from bot_strava.models import User
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