import asyncio
import httpx
import logging

from datetime import datetime
from contextlib import suppress
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists

from bot_strava.models import DieHardPromo
from web_server.database import StravaSessionLocal

URL = "https://diehard.run/api/trpc/promo.findMany?batch=1&input=%7B%220%22%3A%7B%22json%22%3A%7B%22orderBy%22%3A%5B%7B%22startDate%22%3A%22desc%22%7D%5D%7D%7D%7D"
CHECK_INTERVAL = 600

logger = logging.getLogger(__name__)

async def fetch_promos():
    async with httpx.AsyncClient() as client:
        response = await client.get(URL)
        response.raise_for_status()
        return response.json()

async def promo_exists(session: AsyncSession, promo_id: int) -> bool:
    stmt = select(
        exists().where(DieHardPromo.promo_id == promo_id)
    )

    result = await session.execute(stmt)
    return result.scalar()


class PromoWatcher:

    def __init__(self, bot, chat_id: int):
        self.bot = bot
        self.chat_id = chat_id
        self._task: asyncio.Task | None = None

    async def _watcher_loop(self):
        try:
            while True:
                try:
                    data = await fetch_promos()
                    items = data[0]["result"]["data"]["json"]
                    async with StravaSessionLocal() as session:
                        for item in items:
                            if not await promo_exists(session, item['id']):
                                item_date = datetime.fromisoformat(item['endDate'])
                                text = (
                                    f"В магазине DieHard Новый промокод!\n"
                                    f"{item['title']}\n"
                                    f"Баллы: {item['price']}\n"
                                    f"Осталось: {item['_count']['coupons']}\n"
                                    f"Срок до {item_date}"
                                )
                                await self.bot.send_message(self.chat_id, text)

                                promo = DieHardPromo(
                                    promo_id=item['id'],
                                    name=item['title'],
                                    end_date=item_date,
                                    coupons=item['_count']['coupons'],
                                    price=item['price']
                                )
                                session.add(promo)
                                await session.commit()
                except Exception as e:
                    logger.warning("Watcher error:", e)

                await asyncio.sleep(CHECK_INTERVAL)

        except asyncio.CancelledError:
            logger.info("Watcher stopped")
            raise

    def start(self):
        if self._task and not self._task.done():
            return False

        self._task = asyncio.create_task(self._watcher_loop())
        return True

    async def stop(self):
        if not self._task:
            return False

        self._task.cancel()

        with suppress(asyncio.CancelledError):
            await self._task

        self._task = None
        return True

    def is_running(self) -> bool:
        return self._task is not None and not self._task.done()