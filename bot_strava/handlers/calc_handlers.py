import json
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import bot_strava.keyboards as kb


router = Router(name=__name__)

logger = logging.getLogger(__name__)

with open("bot_strava/messages.json", "r", encoding="utf-8") as file:
    messages = json.load(file)


@router.message(Command("calc"))
async def calc_menu(message: Message):
    await message.answer(messages[0]["calc"])


@router.message(Command("result"))
async def result_time(message: Message):
    await message.answer(messages[0]["distance"],
                         reply_markup=await kb.distance_result()
                         )


@router.message(Command("pace"))
async def result_time(message: Message):
    await message.answer(messages[0]["distance"],
                         reply_markup=await kb.distance_pace()
                         )