import re

from aiogram.types import Message
from gspread import Worksheet


async def upload_stock_to_sheet(sheet: Worksheet, data: dict) -> None:
    if any(data.values()):
        sheet.add_rows(len(data["hidden"]) + 1)

        last_row: int = len(sheet.get("A3:A")) + 4

        sheet.batch_update(
            data=[
                {"range": f"A{last_row}", "values": data["hidden"]},
                {"range": f"J{last_row}", "values": data["visible"]},
            ],
        )


async def prepare_table_data(data: list):

    table_data: dict = {}
    hiden_columns = []
    visible_columns = []

    for tire in data:

        try:
            diameter: float = float(re.sub(r"[a-zA-Z]", "", tire["diameter"]))
        except ValueError:
            diameter = ""
        hidden_row = [
            tire["cae"],
            tire["width"],
            tire["height"],
            diameter,
            tire["season"],
        ]

        brand_and_model = tire["brand"] + " " + tire["model"]
        size = f"{tire["width"]}/{tire["height"]}{tire["diameter"]} {tire["load_index"]}{tire["speed_index"]}"
        visible_row = [brand_and_model, size]

        hiden_columns.append(hidden_row)
        visible_columns.append(visible_row)

    table_data["hidden"] = hiden_columns
    table_data["visible"] = visible_columns

    return table_data


async def sort_stock(data):
    sorted_data = sorted(
        data,
        key=lambda x: (
            x["brand"],
            x["model"],
            x["diameter"],
            x["width"],
            x["height"],
        ),
    )
    return sorted_data


async def append_rows(sheet: Worksheet, stock: list, message: Message) -> None:
    """Вносит новые позиции в таблицу.\n"""

    #  stock -> [{'cae': 'F7640', 'name': 'P215/65R17 98T ...', 'season': 'Зимняя', ...}, {}, {}]

    ex_caes: list = [item[0] if item else "" for item in sheet.get("A3:A")]
    #  ['F2057', 'R5601', '', 'R1252', ...]
    fresh_stock: list = [line for line in stock if line["cae"] not in ex_caes]
    await message.answer(f"✅ Найдено новых позиций: <b>{len(fresh_stock)}</b> шт.")

    if len(fresh_stock) > 0:

        sorted_fresh_stock: list = await sort_stock(fresh_stock)
        await message.answer("✅ Новые позиции отсортированы по Модели и Маркировке.")

        table_data = await prepare_table_data(data=sorted_fresh_stock)
        #  {'hidden': [['', 215, 55, 16,'Всесезонная'], []], 'visible': [[], []]}
        await message.answer("✅ Данные подготовлены для добавления в таблицу.")

        await upload_stock_to_sheet(sheet=sheet, data=table_data)
