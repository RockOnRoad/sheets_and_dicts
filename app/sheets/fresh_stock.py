import asyncio
import random
from typing import Any
from aiogram.types import Message, CallbackQuery

from gspread import Worksheet
from gspread.exceptions import APIError
from app.services import MessageAnimation

from . import BASE_LAYOUT, STC

MAX_RETRIES = 8
BASE_DELAY = 1  # seconds


async def prepare_table_data(data: list[dict[str, Any]]) -> dict[str, list[Any]]:
    """**Returns table-ready grid of SKUs (stock keeping units)**

    This function prepares data for new stock units to be added to the worksheet.\n
    It processes the input data and formats it into a dictionary containing two lists:
    - `hidden`: Contains parameters for columns that will be hidden.
    - `visible`: Contains attributes that will be shown.\n


    :param data: `list[dict[str, Any]]` - List of stock objects to be processed.\n
    :return: `dict[list[list[Any]]]` - 2 lists of lists with data for new stock units.\n
    - `{'hidden': [[],[]], 'visible': [[],[]]}`
    - Outer list represents the whole block, inner lists are rows of parameters for each SKU.
    """

    table_data: dict[str, list[Any]] = {"hidden": [], "visible": []}
    for line in data:

        hidden_row = [
            line["art"],
            line["width"],
            line["hei"],
            line["diam"],
            line["siz"],
            line["lt"],
            line["seas"],
            line["stud"],
            line["supp"],
            line.get("local_art", ""),
            line.get("text", ""),
        ]
        visible_row = [line["name"], line["full_size"], line.get("age", "")]

        table_data["hidden"].append(hidden_row)
        table_data["visible"].append(visible_row)

    return table_data


async def sort_stock(data: list[dict[str, Any]]):

    def _parse_height(value):
        if value in ("", None):
            return float("inf")  # put empty at the end
        try:
            return float(str(value).replace(",", "."))
        except ValueError:
            return float("inf")

    sorted_data: list[dict[str, Any]] = list()
    if len(data) > 0:
        sorted_data = sorted(
            data,
            key=lambda x: (
                x["lt"],
                x["name"],
                x["diam"],
                x["width"],
                _parse_height(x.get("hei")),
                x.get("full_code", ""),
            ),
        )
    return sorted_data


async def add_new_items(
    upd: Message | CallbackQuery, stock: list[dict[str, Any]], ws: Worksheet, supp: str
) -> list:
    """**Adds new stock items to the supplier worksheet.**

    :param stock: `list[dict[str, Any]]` - List of stock objects.
    :param ws: `gspread.Worksheet` - Worksheet instance where the SKUs will be added.
    :param supp: `str` - Name of supplier for correct dependancies

    :return: `list` - List of hidden parameters.
    """
    # fresh_stock: list[dict[str, Any]] = await fresh(stock, table=supp, supp=supp)
    if stock:
        sorted_stock: list[dict[str, Any]] = await sort_stock(stock)
        prepared_stock: dict[str, list[Any]] = await prepare_table_data(sorted_stock)

        msg_animation_1 = MessageAnimation(
            message_or_call=upd,
            base_text=f"<b>{supp}</b> запись - создание пустых строк",
        )
        await msg_animation_1.start()

        #  Добавляем достаточное кол-во строк чтобы вместить новые SKU
        ws.add_rows(len(prepared_stock["hidden"]) + 1)

        await msg_animation_1.stop()

        msg_animation_2 = MessageAnimation(
            message_or_call=upd,
            base_text=f"<b>{supp}</b> чтение - номер последней заполненной строки",
        )
        await msg_animation_2.start()

        # try:
        # number_last_row = len(ws.col_values(1)) + 2

        for attempt in range(MAX_RETRIES):
            try:
                number_last_row = len(ws.col_values(1)) + 2
                break

            except APIError:
                # If it's the last attempt – rethrow
                if attempt == MAX_RETRIES - 1:
                    raise

                # Exponential backoff + jitter
                delay = BASE_DELAY * (2**attempt)
                delay += random.uniform(0, 0.5)

                await asyncio.sleep(delay)
        # except APIError as e:
        #     print(
        #         f"Не получилось получить номер последней строки в таблице {supp}\nОшибка: {e}"
        #     )
        #     raise e

        await msg_animation_2.stop()

        _l_art: str = BASE_LAYOUT["art"]["l"]
        _l_name: str = STC[supp]["name"]["l"]

        msg_animation_3 = MessageAnimation(
            message_or_call=upd,
            base_text=f"<b>{supp}</b> запись - новых позиций",
        )
        await msg_animation_3.start()

        ws.batch_update(
            data=[
                {
                    "range": f"{_l_art}{number_last_row}",
                    "values": prepared_stock["hidden"],
                },
                {
                    "range": f"{_l_name}{number_last_row}",
                    "values": prepared_stock["visible"],
                },
            ],
        )

        await msg_animation_3.stop()

        print("Batch update complete")
    return prepared_stock["hidden"]
