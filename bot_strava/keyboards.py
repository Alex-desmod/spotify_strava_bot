import logging
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from enum import Enum

from bot_strava.config import get_auth_link


logger = logging.getLogger(__name__)


async def authorize(tg_id):
    auth_link = get_auth_link(tg_id)
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="🔗 Авторизоваться в Strava", url=auth_link))
    return kb.as_markup()


async def start():
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Неделя", callback_data="week"))
    kb.add(InlineKeyboardButton(text="Месяц", callback_data="month"))
    kb.add(InlineKeyboardButton(text="Год", callback_data="year"))
    return kb.adjust(1).as_markup()


cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True,
    one_time_keyboard=True
)