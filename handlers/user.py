from ast import parse
import asyncio
from hashlib import new
from operator import call
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

import calendar
from datetime import datetime, timedelta

    
@dp.message(Command('start'))
async def start_message_handler(message: Message, state: FSMContext):
    await state.clear()
    
    if await Orm.get_user_by_telegram_id(message.from_user.id):
        return await send_start_message(message)
    
    msg = message.text[7:]
    print(msg)
    if msg == 'paid':
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
async def birth_date_callback_handler(callback: CallbackQuery, state: FSMContext):
    await bot.send_message(
        chat_id=callback.from_user.id,
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
    await callback.message.delete_reply_markup()
    action = callback.data.split(':')[-1]
    if action == 'confirm':
        data = await state.get_data()
        date = data.get('date')
        await Orm.update_birth_date(callback.from_user.id, date)
        
        await callback.message.answer(
            text=confirmed_date_text,
            reply_markup=start_calculate_markup
        )
        
        await state.clear()
        
    elif action == 'decline':
        await callback.message.answer(
            text=birth_date_text
        )
        
@dp.callback_query(F.data == 'calculate')
async def calculate_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    answer = await callback.message.answer(
        text=start_calculating_text
    )
    
    await asyncio.sleep(3)
    user = await Orm.get_user_by_telegram_id(callback.from_user.id)
    birth_date = user.birth_date
    e, a, b, c, d, f, g, h, i, j = await calculate(birth_date)
    l = await calculate(birth_date)
    print(l)
    
    await answer.delete()
    captions = await generate_calculating_completed_text(a, b, c, d, e, f, g, h, i ,j)
    await callback.message.answer_photo(
        photo="AgACAgIAAxkBAAIwBmcagDpmmqQOplEymerlcrAOucY8AAKO3jEbWVbRSBQo17LpCH_zAQADAgADeQADNgQ",
        caption=captions[0],
        reply_markup=await generate_letter_keyboard('e', e),
        parse_mode="markdown"
    )
    
    await callback.message.answer(
        text=captions[1],
        parse_mode="markdown"
    )
    
    await state.update_data(
        a=a, b=b, c=c, d=d, e=e, f=f, g=g, h=h, i=i, j=j
    )
    
    
@dp.callback_query(lambda callback: callback.data.startswith('letter:'))
async def letter_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    user = await Orm.get_user_by_telegram_id(callback.from_user.id)
    birth_date = user.birth_date
    _, letter, number = callback.data.split(':')
    imp_text, text = await get_letter_text(letter, number)
    await callback.message.answer(
        text=imp_text,
    )
    l = await calculate(birth_date)
    new_letter_number = await get_index_of_value_in_list(list_of_letter, letter) + 1
    if new_letter_number == 10:
        return await callback.message.answer(
            text=text
        )
    await asyncio.sleep(3)
    await callback.message.answer(
        text=text,
        reply_markup=await generate_letter_keyboard(list_of_letter[new_letter_number], l[new_letter_number])
    )
    
async def get_index_of_value_in_list(l, value):
    for i, v in enumerate(l):
        if v == value:
            return i
    return None
    
async def calculate(birth_date: datetime):
    day, month, year = await calculate_year_date()
    # а
    a = await sum_digits_until_22(day + birth_date.day)
    # б
    b = await sum_digits_until_22(month + birth_date.month)
    # в
    c = await sum_digits_until_22(year + birth_date.year)
    # г
    d = await sum_digits_until_22(a + b + c)
    # д
    e = await sum_digits_until_22(a + b + c + d)
    # е
    f = await sum_digits_until_22(a + b)
    # ё
    g = await sum_digits_until_22(b + c)
    # ж
    h = await sum_digits_until_22(c + d)
    # з
    i = await sum_digits_until_22(d + a)
    # к
    j = await sum_digits_until_22(a + b + c + d + e + f + g  + h + i)
    return e, a, b, c, d, f, g, h, i, j
    
    
async def calculate_year_date():
    now = datetime.now() + timedelta(days=30*3)
    year_sum = sum(map(int, [c for c in str(now.year)]))
    year = await sum_digits_until_22(year_sum)
    month = await sum_digits_until_22(12 + year)
    day = await sum_digits_until_22(await days_in_current_year(now))
    return 14, 21, 2025

async def days_in_current_year(now):
    return 366 if calendar.isleap(now.year) else 365
    
async def sum_digits_until_22(number: int):
    while number > 22:
        number = sum(int(digit) for digit in str(number))
    return number

@dp.callback_query(F.data == 'close')
async def close_callback(callback: CallbackQuery):
    await callback.message.delete()