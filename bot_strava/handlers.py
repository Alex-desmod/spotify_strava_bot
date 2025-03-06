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

#current moment in the timestamp format
current_epoch = int(datetime.now().timestamp())

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
    await  callback.message.answer(messages[0]["else"],
                             reply_markup=await kb.start())


@router.callback_query(F.data == "month")
async def week(callback: CallbackQuery):
    await callback.answer()
    start_of_month = date(date.today().year, date.today().month, 1)
    start_of_month_datetime = datetime.combine(start_of_month, time.min)
    start_of_month_epoch = int(start_of_month_datetime.timestamp())
    if date.today().month == 1:  # In case of January
        start_of_last_month = date(date.today().year - 1, 12, 1)
    else:
        start_of_last_month = date(date.today().year, date.today().month - 1, 1)
    start_of_last_month_datetime = datetime.combine(start_of_last_month, time.min)
    start_of_last_month_epoch = int(start_of_last_month_datetime.timestamp())

    current_month_data = []
    last_month_data = []

    for i in range(1, 10):
        current_month_response = await crud.get_activities(callback.from_user.id,
                                                           current_epoch,
                                                           start_of_month_epoch,
                                                           page=i)
        last_month_response = await crud.get_activities(callback.from_user.id,
                                                           start_of_month_epoch,
                                                           start_of_last_month_epoch,
                                                           page=i)
        if not current_month_response and not last_month_response:
            break
        current_month_data += current_month_response
        last_month_data += last_month_response

    current_month_distance = {"Run": 0, "Ride": 0, "Walk": 0, "NordicSki": 0, "Swim": 0}
    last_month_distance = {"Run": 0, "Ride": 0, "Walk": 0, "NordicSki": 0, "Swim": 0}
    current_month_ride_elevation = 0
    last_month_ride_elevation = 0

    run_workouts = [act for act in current_month_data if act["type"] == "Run" and act["workout_type"] == 3] + [act for act in last_month_data if act["type"] == "Run" and act["workout_type"] == 3]
    ride_workouts = [act for act in current_month_data if act["type"] == "Ride" and act["workout_type"] == 12] + [act for act in last_month_data if act["type"] == "Ride" and act["workout_type"] == 12]

    for act in current_month_data:
        if act["type"] in current_month_distance.keys():
            current_month_distance[act["type"]] += act["distance"]

            if act["type"] == "Ride":
                current_month_ride_elevation += act["total_elevation_gain"]

    for act in last_month_data:
        if act["type"] in last_month_distance.keys():

            last_month_distance[act["type"]] += act["distance"]

            if act["type"] == "Ride":
                last_month_ride_elevation += act["total_elevation_gain"]

    await callback.message.answer(f"<b>Бег</b> 🏃‍➡️\nТекущий месяц: {current_month_distance['Run']/1000:.1f} км\n"
                                  f"Прошлый месяц: {last_month_distance['Run']/1000:.1f} км")
    if run_workouts:
        await callback.message.answer(messages[0]["workouts"])
        for workout in run_workouts:
            workout_time = str(timedelta(seconds=workout["moving_time"]))
            full_workout = await crud.get_the_activity(callback.from_user.id, workout["id"])
            await callback.message.answer(f"<b>{workout['start_date'].split('T')[0]}</b> "
                                          f"{workout['name']}\n{workout['distance'] / 1000:.1f} км {workout_time}\n"
                                          f"{full_workout['description']}")

    await callback.message.answer(f"<b>Вело</b> 🚴‍\nТекущий месяц: {current_month_distance['Ride'] / 1000:.1f} км\n"
                                  f"набор высоты ↗️{int(current_month_ride_elevation)} м\n\n"
                                  f"Прошлый месяц: {last_month_distance['Ride'] / 1000:.1f} км\n"
                                  f"набор высоты ↗️{int(last_month_ride_elevation)} м")
    if ride_workouts:
        await callback.message.answer(messages[0]["workouts"])
        for workout in ride_workouts:
            workout_time = str(timedelta(seconds=workout["moving_time"]))
            full_workout = await crud.get_the_activity(callback.from_user.id, workout["id"])
            await callback.message.answer(f"<b>{workout['start_date'].split('T')[0]}</b> "
                                          f"{workout['name']}\n{workout['distance'] / 1000:.1f} км {workout_time}\n"
                                          f"{full_workout['description']}")

    if current_month_distance['Walk'] > 0:
        await callback.message.answer(f"<b>Ходьба</b>🚶‍➡️\nТекущий месяц: {current_month_distance['Walk'] / 1000:.1f} км\n"
                                      f"Прошлый месяц: {last_month_distance['Walk'] / 1000:.1f} км")
    if current_month_distance['NordicSki'] > 0:
        await callback.message.answer(f"<b>Лыжи</b>\nТекущий месяц: {current_month_distance['NordicSki'] / 1000:.1f} км\n"
                                      f"Прошлый месяц: {last_month_distance['NordicSki'] / 1000:.1f} км")
    if current_month_distance['Swim'] > 0:
        await callback.message.answer(f"<b>Плавание</b>🏊‍➡️\nТекущий месяц: {current_month_distance['Swim'] / 1000:.1f} км\n"
                                      f"Прошлый месяц: {last_month_distance['Swim'] / 1000:.1f} км")
    await  callback.message.answer(messages[0]["else"],
                                   reply_markup=await kb.start())


@router.callback_query(F.data == "year")
async def week(callback: CallbackQuery):
    await callback.answer()

    start_of_year = date(date.today().year, 1, 1)
    start_of_year_datetime = datetime.combine(start_of_year, time.min)
    start_of_year_epoch = int(start_of_year_datetime.timestamp())

    total_data = await crud.get_total(callback.from_user.id)
    current_year_data = []
    for i in range(1, 12):
        current_year_response = await crud.get_activities(callback.from_user.id,
                                                           current_epoch,
                                                           start_of_year_epoch,
                                                           page=i)
        if not current_year_response:
            break
        current_year_data += current_year_response

    run_races = [race for race in current_year_data if race["type"] == "Run" and race["workout_type"] == 1]
    ride_races = [race for race in current_year_data if race["type"] == "Ride" and race["workout_type"] == 11]

    await callback.message.answer(f"<b>Бег</b> 🏃‍➡️\n"
                                  f"Текущий год: {total_data['ytd_run_totals']['distance']/1000:.1f} км")
    if run_races:
        await callback.message.answer(messages[0]["races"])
        for race in run_races:
            race_time = str(timedelta(seconds=race["moving_time"]))
            await callback.message.answer(f"<b>{race['start_date'].split('T')[0]}</b> "
                                          f"{race['name']}\n{race['distance']/1000:.1f} км {race_time}")
        await  callback.message.answer(messages[0]["else"],
                                       reply_markup=await kb.start())

    await callback.message.answer(f"<b>Вело</b> 🚴‍\n"
                                  f"Текущий год: {total_data['ytd_ride_totals']['distance'] / 1000:.1f} км")
    if ride_races:
        await callback.message.answer(messages[0]["races"])
        for race in ride_races:
            race_time = str(timedelta(seconds=race["moving_time"]))
            await callback.message.answer(f"<b>{race['start_date'].split('T')[0]}</b> "
                                          f"{race['name']}\n{race['distance']/1000:.1f}км {race_time}")
        await  callback.message.answer(messages[0]["else"],
                                       reply_markup=await kb.start())


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