import logging
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from enum import Enum

import endpoints

logger = logging.getLogger(__name__)

class Time_range(Enum):
    SHORT_TERM = "Последний месяц"
    MEDIUM_TERM = "Полгода"
    LONG_TERM = "All-time 🐐"


class Limit(Enum):
    TEN = 10
    TWENTY = 20
    FIFTY = 50


async def authorize(tg_id):
    auth_link = endpoints.get_auth_link(tg_id)
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="🔗 Авторизоваться в Spotify", url=auth_link))
    return kb.as_markup()


async def start():
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Top artists", callback_data="artists"))
    kb.add(InlineKeyboardButton(text="Top tracks", callback_data="tracks"))
    return kb.adjust(1).as_markup()


async def times(entity):
    kb = InlineKeyboardBuilder()
    for term in Time_range:
        kb.add(InlineKeyboardButton(text=term.value, callback_data=f"{entity}.{term.name.lower()}"))
        # logger.info(entity)
    kb.add(InlineKeyboardButton(text="Главное меню 🔙", callback_data='back'))
    return kb.adjust(1).as_markup()


async def limits(entity):
    kb = InlineKeyboardBuilder()
    for lim in Limit:
        kb.add(InlineKeyboardButton(text=f"Top-{lim.value}", callback_data=f"{entity}.{lim.value}"))
        # logger.info(entity)
    kb.add(InlineKeyboardButton(text="Главное меню 🔙", callback_data='back'))
    return kb.adjust(3).as_markup()


cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True,
    one_time_keyboard=True
)