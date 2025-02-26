import json
import logging

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
        await message.answer(messages[0]["top"],
                             reply_markup=await kb.start())