import asyncio
from aiogram import F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery, FSInputFile
)

from bot import dp, bot

from models.dbs.orm import Orm
from models.dbs.models import *

from .callbacks import *
from .markups import *
from .states import *

from datetime import datetime

@dp.message(Command('start'))
async def start_message_handler(message: Message, state: FSMContext):
    await state.clear()
    
    await Orm.create_user(message)
    await send_start_message(message)
    
async def send_start_message(message: Message):
    await bot.send_message(
        chat_id=message.from_user.id,
        text=await generate_start_text(message),
    )
    
    await asyncio.sleep(3)
    
    await bot.send_message(
        chat_id=message.from_user.id,
        text=second_start_text,
        reply_markup=start_markup
    )
    
@dp.callback_query(F.data == 'birth_date')
async def birth_date_callback_handler(callback_query: CallbackQuery, state: FSMContext):
    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text=birth_date_text
    )
    await state.set_state(UserStates.birth_date)
    
async def is_valid_date(string: str):
    try:
        datetime.strptime(string, '%d.%m.%Y')
        return True
    except Exception:
        return False
    
@dp.message(UserStates.birth_date)
async def get_birth_date(message: Message, state: FSMContext):
    text = message.text
    if await is_valid_date(text):
        date = datetime.strptime(text, '%d.%m.%Y')
        await state.update_data(date=date)

        await message.answer(
            text=await is_your_birth_date_correct_text(text),
            reply_markup=confirm_date_markup
        )
    else:
        await message.answer(
            text=incorrect_date_format_text
        )
    
@dp.callback_query(lambda callback_query: callback_query.data.startswith('date:'))
async def confirm_or_decline_date_callback(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split(':')[-1]
    if action == 'confirm':
        data = await state.get_data()
        date = data.get('date')
        await Orm.update_birth_date(callback.from_user.id, date)
        
        await callback.message.answer(
            text=
        )
        
    elif action == 'decline':
        await callback.message.answer(
            text=birth_date_text
        )