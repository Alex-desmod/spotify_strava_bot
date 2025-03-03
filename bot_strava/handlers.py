import json
import logging
from datetime import datetime, date, timedelta, time

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

import bot_strava.keyboards as kb
import bot_strava.crud as crud


router = Router(name=__name__)

logger = logging.getLogger(__name__)

with open("bot_strava/messages.json", "r", encoding="utf-8") as file:
    messages = json.load(file)


#Defining the state for feedback
class FeedbackState(StatesGroup):
    waiting_for_feedback = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await crud.set_user(message.from_user.id, message.from_user.first_name)
    access_token = await crud.get_valid_access_token(message.from_user.id)
    # logger.info(access_token)
    if not access_token:
        await message.answer(f'Привет, {message.from_user.first_name} 😊\n{messages[0]["start"]}',
                         reply_markup=await kb.authorize(message.from_user.id))
    else:
        await message.answer(messages[0]["main"],
                             reply_markup=await kb.start())


@router.callback_query(F.data == "week")
async def week(callback: CallbackQuery):
    await callback.answer()
    current_epoch = int(datetime.now().timestamp())
    start_of_week = date.today() - timedelta(days=date.today().weekday())
    start_of_week_datetime = datetime.combine(start_of_week, time.min)
    start_of_week_epoch = int(start_of_week_datetime.timestamp())
    start_of_last_week = start_of_week - timedelta(days=7)
    start_of_last_week_datetime = datetime.combine(start_of_last_week, time.min)
    start_of_last_week_epoch = int(start_of_last_week_datetime.timestamp())

    current_week_data = await crud.get_activities(callback.from_user.id, current_epoch, start_of_week_epoch)
    last_week_data = await crud.get_activities(callback.from_user.id, start_of_week_epoch, start_of_last_week_epoch)

    current_week_distance ={"Run": 0, "Ride": 0,  "Walk": 0, "NordicSki": 0, "Swim": 0}
    last_week_distance = {"Run": 0, "Ride": 0, "Walk": 0, "NordicSki": 0, "Swim": 0}
    current_week_ride_elevation = 0
    last_week_ride_elevation = 0

    for act in current_week_data:
        if act["type"] in current_week_distance.keys():
            current_week_distance[act["type"]] += act["distance"]

            if act["type"] == "Ride":
                current_week_ride_elevation += act["total_elevation_gain"]

    for act in last_week_data:
        if act["type"] in last_week_distance.keys():

            last_week_distance[act["type"]] += act["distance"]

            if act["type"] == "Ride":
                last_week_ride_elevation += act["total_elevation_gain"]

    await callback.message.answer(f"<b>Бег</b> 🏃‍➡️\nТекущая неделя: {current_week_distance['Run']/1000:.1f} км\n"
                                  f"Прошлая неделя: {last_week_distance['Run']/1000:.1f} км")
    await callback.message.answer(f"<b>Вело</b> 🚴‍\nТекущая неделя: {current_week_distance['Ride'] / 1000:.1f} км\n"
                                  f"набор высоты ↗️{int(current_week_ride_elevation)} м\n\n"
                                  f"Прошлая неделя: {last_week_distance['Ride'] / 1000:.1f} км\n"
                                  f"набор высоты ↗️{int(last_week_ride_elevation)} м")
    if current_week_distance['Walk'] > 0:
        await callback.message.answer(f"<b>Ходьба</b>🚶‍➡️\nТекущая неделя: {current_week_distance['Walk'] / 1000:.1f} км\n"
                                      f"Прошлая неделя: {last_week_distance['Walk'] / 1000:.1f} км")
    if current_week_distance['NordicSki'] > 0:
        await callback.message.answer(f"<b>Лыжи</b>\nТекущая неделя: {current_week_distance['NordicSki'] / 1000:.1f} км\n"
                                      f"Прошлая неделя: {last_week_distance['NordicSki'] / 1000:.1f} км")
    if current_week_distance['Swim'] > 0:
        await callback.message.answer(f"<b>Плавание</b>🏊‍➡️\nТекущая неделя: {current_week_distance['Swim'] / 1000:.1f} км\n"
                                      f"Прошлая неделя: {last_week_distance['Swim'] / 1000:.1f} км")






@router.message(Command("feedback"))
async def ask_feedback(message: Message, state: FSMContext):
    await message.answer(messages[0]["feedback"],
                         reply_markup=kb.cancel_kb
                         )
    await state.set_state(FeedbackState.waiting_for_feedback)


@router.message(FeedbackState.waiting_for_feedback, F.text != "❌ Отмена")
async def forward_feedback(message: Message, bot: Bot, state: FSMContext):
    admins = await crud.get_admins()

    for admin in admins:
        logger.info(admin.tg_id)
        await bot.send_message(
            admin.tg_id,
            f"📩 Новое сообщение от @{message.from_user.username or message.from_user.id}:\n\n{message.text}"
        )
    await message.answer(messages[0]["send"], reply_markup=ReplyKeyboardRemove())
    await state.clear()


@router.message(FeedbackState.waiting_for_feedback, F.text == "❌ Отмена")
async def cancel_feedback(message: Message, state: FSMContext):
    await message.answer(messages[0]["canceled"], reply_markup=ReplyKeyboardRemove())
    await state.clear()


@router.message()
async def catch_all_messages(message: Message):
    await message.answer(messages[0]["sorry"],
                         reply_markup=await kb.start())