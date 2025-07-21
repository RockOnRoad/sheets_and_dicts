import random
from datetime import datetime

from aiogram.types import Message
from gspread import Worksheet


async def insert_updated_amounts(sheet: Worksheet, amounts: list) -> None:

    r = float(random.randint(0, 30))
    g = float(random.randint(0, 30))
    b = float(random.randint(0, 30))

    today = datetime.today().strftime("%d.%m")
    sheet.insert_cols([[f"Наличие {today}"], [f"Стоимость {today}"]], col=18)
    sheet.update(amounts, "R3")
    sheet.format("R3:S", {"backgroundColor": {"red": r, "green": g, "blue": b}})
    sheet.update_cell(2, 16, '=ArrayFormula(IF(ISNUMBER(S2:S),S2:S*4,""))')


async def update_amounts(sheet: Worksheet, stock: list, message: Message) -> None:
    wanted_keys: list = ("cae", "rest_kryarsk2", "price_kryarsk2")

    ex_caes: list = [item[0] if item else "" for item in sheet.get("A3:A")]
    #  ['A1AFB03Y', 'T1AFB02Y', '00-00001045', 'AH2038', 'AH2039', ...]
    amounts_data: list = [{k: d.get(k, "") for k in wanted_keys} for d in stock]
    # [{'cae':'F8628', 'rest_kryarsk2': 7, 'price_kryarsk2': 5902},{'cae', 'rest_kryarsk2', 'price_kryarsk2'},{...}]
    await message.answer(
        f"✅ Собранны данные для обновления остатков. <b>{len(amounts_data)}</b> строк."
    )

    stock_lookup = {line["cae"]: line for line in amounts_data}
    #  {'F7640': {'cae': 'F7640', 'rest_kryarsk2': 1, 'price_kryarsk2': 9266}, 'F8628': {'cae': 'F8628', ...}}

    amounts: list = []
    for cae in ex_caes:
        if cae in stock_lookup:
            line = stock_lookup[cae]
            #  {'cae': 'F7640', 'rest_kryarsk2': 1, 'price_kryarsk2': 9266}
            if line.get("rest_kryarsk2", 0) == "более 40":
                line["rest_kryarsk2"] = 40
            amounts.append([line["rest_kryarsk2"], line["price_kryarsk2"]])
        else:
            amounts.append([0, 0])
    #  amounts -> [[1, 53000], [14, 57000], [4, 7700], [20, 3250], ...]
    await message.answer(f"✅ Остатки обновлены. <b>{len(amounts)}</b> строк.")
    await insert_updated_amounts(sheet=sheet, amounts=amounts)
    await message.answer("✅ Остатки и цены добавлены в таблицу.")
