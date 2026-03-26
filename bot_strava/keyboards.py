import logging
from dataclasses import dataclass
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from enum import Enum

from bot_strava.config import get_auth_link


logger = logging.getLogger(__name__)


@dataclass
class Distance:
    label: str
    meters: int

class DistanceEnum(Enum):
    K3 = Distance("3 км", 3000)
    K5 = Distance("5 км", 5000)
    K10 = Distance("10 км", 10000)
    M10 = Distance("16,1 км", 16100)
    HALF = Distance("21,1 км", 21097)
    K30 = Distance("30 км", 30000)
    MARATHON = Distance("42,2 км", 42195)


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


async def distance_result():
    kb = InlineKeyboardBuilder()
    for d in DistanceEnum:
        kb.add(InlineKeyboardButton(text=d.value.label, callback_data=f"result_{d.value.meters}"))
    return kb.adjust(3).as_markup()


async def distance_pace():
    kb = InlineKeyboardBuilder()
    for d in DistanceEnum:
        kb.add(InlineKeyboardButton(text=d.value.label, callback_data=f"pace_{d.value.meters}"))
    return kb.adjust(3).as_markup()


async def numpad():
    kb = InlineKeyboardBuilder()
    for n in range(1,10):
        kb.add(InlineKeyboardButton(text=str(n), callback_data=str(n)))
    kb.add(InlineKeyboardButton(text="0", callback_data="0"))
    return kb.adjust(3).as_markup()


cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True,
    one_time_keyboard=True
)