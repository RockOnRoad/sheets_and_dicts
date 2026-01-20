import asyncio
import random
from typing import Any
from aiogram.types import Message, CallbackQuery

from gspread import Worksheet
from gspread.exceptions import APIError
from app.services import MessageAnimation

from app.sheets.sheety_loops import retryable_and_animated

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

        #  Добавляем достаточное кол-во строк чтобы вместить новые SKU
        await retryable_and_animated(
            upd=upd, base_text=f"<b>{supp}</b> запись - создание пустых строк"
        )(ws.add_rows)(len(prepared_stock["hidden"]) + 1)

        #  Узнаем номер последней заполненной строки
        get_last_row = await retryable_and_animated(
            upd=upd,
            base_text=f"<b>{supp}</b> чтение - номер последней заполненной строки",
        )(lambda: len(ws.col_values(1)) + 2)
        number_last_row: int = await get_last_row()

        _l_art: str = BASE_LAYOUT["art"]["l"]
        _l_name: str = STC[supp]["name"]["l"]

        await retryable_and_animated(
            upd=upd, base_text=f"<b>{supp}</b> запись - новых позиций"
        )(ws.batch_update)(
            data=[
                {
                    "range": f"{_l_art}{number_last_row}",
                    "values": prepared_stock["hidden"],
                },
                {
                    "range": f"{_l_name}{number_last_row}",
                    "values": prepared_stock["visible"],
                },
            ]
        )

        print("Batch update complete")
    return prepared_stock["hidden"]
