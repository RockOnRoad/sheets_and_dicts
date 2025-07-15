from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message


rtr = Router(name=__name__)


@rtr.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Salom, {message.from_user.full_name}!")


@rtr.message(Command("help"))
async def help(message: Message):
    await message.answer("Информация о боте")
