import asyncio
import random
from gspread import Worksheet
from gspread.exceptions import APIError
from aiogram.types import Message, CallbackQuery

from app.services.message_animation import MessageAnimation


#  Этот слой нужен в том случае, когда декоратор принимает аргументы
def retryable_and_animated(
    *,
    upd: Message | CallbackQuery | None = None,
    base_text: str | None = None,
    retries=8,
    base_delay=1,
):
    #  Слой декоратора
    def decorator(fn):
        #  Слой логики
        async def wrapper(*args, **kwargs):

            if base_text:
                msg = MessageAnimation(upd=upd, base_text=base_text)
                await msg.start()

            for attempt in range(retries):
                try:
                    return fn(*args, **kwargs)
                except APIError:
                    if attempt == retries - 1:
                        raise
                    asyncio.sleep(base_delay * (2**attempt) + random.random())

            if base_text:
                await msg.stop()

        return wrapper

    return decorator


# @retryable_and_animated
# async def get_last_row(ws: Worksheet):
#     return len(ws.col_values(1)) + 2
