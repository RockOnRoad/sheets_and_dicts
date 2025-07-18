import re
from gspread import Worksheet
from . import sheets_conn


async def upload_stock_to_sheet(sheet: Worksheet, data: dict) -> None:
    #  Переделать чтобы добавляло в конец

    sheet.update(data["hidden"], "A3")
    sheet.update(data["visible"], "H3")
    sheet.update(data["amounts"], "R3")


async def prepare_table_data(sorted_data):
    data: dict = {}
    hiden_columns = []
    visible_columns = []
    amounts_columns = []

    for tire in sorted_data:

        diameter: int = int(re.sub(r"[^0-9]", "", tire["diameter"]))
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

        if tire.get("rest_kryarsk2", "-") == "более 40":
            rest = 40
        else:
            rest = tire.get("rest_kryarsk2", "-")
        amounts_row = [
            rest,
            tire.get("price_kryarsk2", "-"),
        ]

        hiden_columns.append(hidden_row)
        visible_columns.append(visible_row)
        amounts_columns.append(amounts_row)

    data["hidden"] = hiden_columns
    data["visible"] = visible_columns
    data["amounts"] = amounts_columns

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

    for line in sorted_fresh_stock:
        print(f"{line['cae']}, {line['brand']}, {line['name']}")
    print(len(sorted_fresh_stock))

    # surplus_tires: list = await pick_new_stock(stock, ex_caes)
