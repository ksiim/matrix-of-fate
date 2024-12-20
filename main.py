import asyncio
from datetime import datetime

from bot import dp, bot

import logging

import handlers

from models.databases import create_database


logging.basicConfig(level=logging.INFO)

async def main():
    await handlers.calculate(datetime.now())
    await create_database()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())