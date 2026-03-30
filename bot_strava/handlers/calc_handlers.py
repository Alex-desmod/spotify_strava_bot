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
    waiting_for_result = State()


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
    await callback.message.answer(
        "Введи темп. 3 цифры в формате x:xx мин/км",
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
        if len(digits) == 1:
            await callback.message.edit_text(
                f"Введи темп. 3 цифры в формате {digits[0]}:xx мин/км",
                reply_markup=await kb.numpad()
            )
        else:
            await callback.message.edit_text(
                f"Введи темп. 3 цифры в формате {digits[0]}:{digits[1]}x мин/км",
                reply_markup=await kb.numpad()
            )
    else:
        pace_sec = int(digits[0])*60 + int(digits[1:])
        distance = data["distance"]
        total_sec = pace_sec*(distance/1000)
        hours = total_sec // 3600
        mins = (total_sec % 3600) // 60
        secs = total_sec % 60

        await callback.message.edit_text(
            f"Дистанция: {distance/1000:.1f} км\n"
            f"Темп: {digits[0]}:{digits[1:]} мин/км\n"
            f"Результат: {int(hours)}:{int(mins):02d}:{int(secs):02d}",
            reply_markup=None
        )
        await state.clear()


@router.callback_query(F.data.startswith("result_"))
async def result_input(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    distance = int(callback.data.split("_")[1])
    await state.set_state(CalcState.waiting_for_result)
    await state.update_data(
        distance=distance,
        result_digits="",
        timestamp=datetime.now()
    )
    await callback.message.answer(
        "Введи результат. 5 цифр в формате ч:мм:сс",
        reply_markup=await kb.numpad()
    )
