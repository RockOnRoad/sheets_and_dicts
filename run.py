import logging
import os
import sys

import asyncio

from aiogram import Bot, Dispatcher

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from dotenv import load_dotenv

from app.routers import router as main_router

load_dotenv()


COMMANDS = [
    BotCommand(command="add", description="Добавить выгрузку поставщика"),
    BotCommand(command="help", description="Помощь по командам бота"),
]


async def main():
    dp = Dispatcher()
    dp.include_router(main_router)
    bot = Bot(
        token=os.getenv("TOKEN"),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await bot.set_my_commands(commands=COMMANDS)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
