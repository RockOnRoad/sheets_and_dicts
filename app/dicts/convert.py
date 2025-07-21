from aiogram.types import Message
from gspread import Worksheet

from app.sheets.add_rows import append_rows


async def remove_unnecessary_keys(tires):
    keys_to_remove = (
        "price_kryarsk2_rozn",
        "price_oh_krnekr",
        "price_oh_krnekr_rozn",
        "rest_oh_krnekr",
        "price_oh_bilkal",
        "price_oh_bilkal_rozn",
        "rest_oh_bilkal",
        "price_ok_katsev",
        "price_ok_katsev_rozn",
        "rest_ok_katsev",
        "price_yamka",
        "price_yamka_rozn",
        "rest_yamka",
        "price_dvdv",
        "price_dvdv_rozn",
        "rest_dvdv",
        "gtin",
        "diametr_out",
        "thorn_type",
        "tech",
        "protection",
        "usa",
        "omolog",
        "side",
        "axle",
        "sloy",
        "grip",
        "img_small",
        "img_big_pish",
        "protector_type",
        "market_model_id",
        "brand_info",
        "model_info",
        "num_layers_treadmil",
        "tread_width",
        "initial_tread_depth",
    )
    for line in tires:
        for key in keys_to_remove:
            # line.pop(key, None)
            if key in line:
                del line[key]
    return tires


async def order_and_upload(
    parameter: str, data: list, sheet: Worksheet, message: Message
) -> dict:

    stock_by_param: dict = {}
    for i in data:
        key = i.get(parameter, "-")
        stock_by_param.setdefault(key, []).append(i)
    #  {'Yokohama': [{'cae': 'R0229', 'name': ...}, {}, {}], 'Pirelli_Formula': [{'cae': '2177000', {}, {}], ...}

    if parameter == "season":
        #  stock_by_param ->
        #  {'Зимняя': [{'cae': 'F7640', 'name': ...}, {}, {}], 'Летняя': [{'cae': '2177000', {}, {}], ...}

        await message.answer(
            f"""✅ Позиции рассортированы по сезону.
{'\n'.join([f'{key} ({len(value)} строк)' for key, value in stock_by_param.items()])}"""
        )

        snow_and_ice: list = stock_by_param["Зимняя"] + stock_by_param["Всесезонная"]
        #  [{'cae': 'F7640', 'name': ...}, {}, {}, {'cae': '2177000'}, {}, {}, ...]

        await append_rows(sheet=sheet, stock=snow_and_ice, message=message)
