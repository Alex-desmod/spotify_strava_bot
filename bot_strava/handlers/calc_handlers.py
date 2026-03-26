import json
import logging
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import bot_strava.keyboards as kb


router = Router(name=__name__)

logger = logging.getLogger(__name__)

with open("bot_strava/messages.json", "r", encoding="utf-8") as file:
    messages = json.load(file)


class CalcState(StatesGroup):
    waiting_for_pace = State()


@router.message(Command("calc"))
async def calc_menu(message: Message):
    await message.answer(messages[0]["calc"])


@router.message(Command("result"))
async def result_time(message: Message):
    await message.answer(messages[0]["distance"],
                         reply_markup=await kb.distance_result()
                         )


@router.message(Command("pace"))
async def pace_time(message: Message):
    await message.answer(messages[0]["distance"],
                         reply_markup=await kb.distance_pace()
                         )


@router.callback_query(F.data.startswith("pace_"))
async def pace_input(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    distance = int(callback.data.split("_")[1])
    await state.set_state(CalcState.waiting_for_pace)
    await state.update_data(
        distance=distance,
        pace_digits="",
        timestamp=datetime.now()
    )
    await callback.message.answer("Введи темп. 3 цифры в формате x:xx мин/км",
                                  reply_markup=await kb.numpad()
                                  )


@router.callback_query(CalcState.waiting_for_pace, F.data.in_([str(n) for n in range(10)]))
async def handle_pace(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    # timeout check (15 seconds)
    elapsed = (datetime.now() - data["timestamp"]).total_seconds()
    if elapsed > 15:
        await state.clear()
        return

    digits = data.get("pace_digits", "") + callback.data

    if len(digits) < 3:
        await state.update_data(pace_digits=digits, timestamp=datetime.now())
