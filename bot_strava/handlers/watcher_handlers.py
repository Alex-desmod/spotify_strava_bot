import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot_strava.filters.admin import AdminFilter
from bot_strava.services.promocatcher import PromoWatcher

router = Router(name=__name__)

logger = logging.getLogger(__name__)


@router.message(Command("watcher_start"), AdminFilter())
async def start_watcher(message: Message, watcher: PromoWatcher):
    if watcher.start():
        await message.answer("✅ Watcher запущен")
    else:
        await message.answer("⚠️ Watcher уже работает")


@router.message(Command("watcher_stop"), AdminFilter())
async def stop_watcher(message: Message, watcher: PromoWatcher):
    if await watcher.stop():
        await message.answer("🛑 Watcher остановлен")
    else:
        await message.answer("⚠️ Watcher не запущен")