import logging
import sys
import asyncio

from aiogram import Dispatcher
from aiogram.types import BotCommand
from dotenv import load_dotenv

from app.config import bot
from app.routers import router as main_router

load_dotenv()


COMMANDS = [
    BotCommand(command="add", description="Добавить выгрузку поставщика"),
    BotCommand(command="help", description="Помощь по командам бота"),
]


async def main():
    dp = Dispatcher()
    dp.include_router(main_router)
    await bot.set_my_commands(commands=COMMANDS)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="\n--- %(levelname)s: %(asctime)s - %(name)s ---\n%(message)s",
    )
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
