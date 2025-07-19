import random
import re
from datetime import datetime

from gspread import Worksheet
from . import sheets_conn


async def insert_updated_amounts(sheet, stock):

    r = float(random.randint(0, 30))
    g = float(random.randint(0, 30))
    b = float(random.randint(0, 30))

    today = datetime.today().strftime("%d.%m")
    sheet.insert_cols([[f"Наличие {today}"], [f"Стоимость {today}"]], col=18)
    sheet.update(stock, "R3")
    sheet.format("R3:S", {"backgroundColor": {"red": r, "green": g, "blue": b}})
    sheet.update_cell(2, 16, '=ArrayFormula(IF(ISNUMBER(S2:S),S2:S*4,""))')


async def fresh_amounts(sheet, stock):
    amounts: list = []
    caes: list = [item[0] if item else "" for item in sheet.get("A3:A")]

    for cae in caes:
        not_in_stock = True
        for line in stock:
            line_list = []
            if line["cae"] == cae:
                line = stock.pop(stock.index(line))
                if line.get("rest_kryarsk2", "-") == "более 40":
                    rest = 40
                else:
                    rest = line.get("rest_kryarsk2", "-")
                line_list.append(rest)
                line_list.append(line.get("price_kryarsk2", "-"))
                amounts.append(line_list)
                not_in_stock = False
                break
        if not_in_stock:
            amounts.append(["-", "-"])
    return amounts


async def upload_stock_to_sheet(sheet: Worksheet, data: dict) -> None:
    last_row: int = len(sheet.get("A3:A")) + 3

    sheet.update(data["hidden"], f"A{last_row}")
    sheet.update(data["visible"], f"H{last_row}")
    # sheet.update(data["amounts"], f"R{last_row}")


async def prepare_table_data(sorted_data):
    #  Добавлять amounts после всего остального

    data: dict = {}
    hiden_columns = []
    visible_columns = []
    # amounts_columns = []

    for tire in sorted_data:

        diameter: str = float(re.sub(r"[a-zA-Z]", "", tire["diameter"]))
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

        # if tire.get("rest_kryarsk2", "-") == "более 40":
        #     rest = 40
        # else:
        #     rest = tire.get("rest_kryarsk2", "-")
        # amounts_row = [
        #     rest,
        #     tire.get("price_kryarsk2", "-"),
        # ]

        hiden_columns.append(hidden_row)
        visible_columns.append(visible_row)
        # amounts_columns.append(amounts_row)

    data["hidden"] = hiden_columns
    data["visible"] = visible_columns
    # data["amounts"] = amounts_columns

    return data


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


async def seporate_stock(stock, ex_caes) -> list:
    existing: list = []
    fresh: list = []
    for obj in stock:
        if obj["cae"] in ex_caes:
            existing.append(obj)
        else:
            fresh.append(obj)
    return (existing, fresh)


async def populate_sheet(sheet: str = None, stock: list = None) -> None:
    # stock -> [{'cae': 'F7640', 'name': 'P215/65R17 98T ...', 'season': 'Зимняя', ...}, {}, {}]
    stock_sheet: Worksheet = await sheets_conn(sheet)

    ex_caes: list = [item[0] if item else "" for item in stock_sheet.get("A3:A")]
    # ['F2057', 'R5601', '', 'R1252', ...]
    sep_stock: list = await seporate_stock(stock=stock, ex_caes=ex_caes)
    sorted_fresh_stock: list = await sort_stock(sep_stock[1])

    table_data = await prepare_table_data(sorted_fresh_stock)
    await upload_stock_to_sheet(sheet=stock_sheet, data=table_data)

    amounts = await fresh_amounts(sheet=stock_sheet, stock=stock)
    await insert_updated_amounts(sheet=stock_sheet, stock=amounts)

    for line in sorted_fresh_stock:
        print(f"{line['cae']}, {line['brand']}, {line['name']}")
    print(len(sorted_fresh_stock))

    # surplus_tires: list = await pick_new_stock(stock, ex_caes)
