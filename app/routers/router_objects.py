import os

from aiogram.filters.callback_data import CallbackData
from aiogram.filters import Filter
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery


class AdminCheck(Filter):
    """Filter to check if the user is an admin (owner) of the bot."""

    async def __call__(self, update: Message | CallbackQuery) -> bool:
        return str(update.from_user.id) in os.getenv("ADMINS")


class Supplier_Msg_Add(CallbackData, prefix="supp_add"):
    """Assembles inline keyboard of suppliers after user **types /add**"""

    name: str


class Supplier_Msg_State(StatesGroup):
    """**Holds the name of a supplier user chose to /add**"""

    add_command = State()


class Supplier_File_Add(CallbackData, prefix="supp_file_add"):
    """Assembles inline keyboard of suppliers after user **sends a random file**"""

    name: str


class Supplier_File_State(StatesGroup):
    """**Holds the name of a supplier user chose after sending a file**"""

    file = State()
