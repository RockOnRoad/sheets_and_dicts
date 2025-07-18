import json
from io import BytesIO
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery

from app.dicts.convert import arange_by_brand, arange_by_season
from app.sheets.edit_sheets import populate_sheet


rtr = Router()


@rtr.message(F.document)
async def handle_json_file(message: Message):
    if not message.document.file_name.endswith(".json"):
        await message.reply("Только .json файлы поддерживаются.")
        return

    file_obj = BytesIO()
    await message.bot.download(message.document.file_id, destination=file_obj)
    file_obj.seek(0)

    try:
        data = json.load(file_obj)
    except Exception as e:
        await message.reply(f"Invalid JSON: {e}")
        return

    # stock_ordered_by_brand: dict = await arange_by_brand(data)
    # {'Yokohama': [{'cae': 'R0229', 'name': ...}, {}, {}], 'Pirelli_Formula': [{'cae': '2177000', {}, {}], ...}

    stock_ordered_by_season: dict = await arange_by_season(data)
    # {'Зимняя': [{'cae': 'F7640', 'name': ...}, {}, {}], 'Летняя': [{'cae': '2177000', {}, {}], ...}

    snow_and_ice_stock: list = (
        stock_ordered_by_season["Зимняя"] + stock_ordered_by_season["Всесезонная"]
    )

    await populate_sheet(sheet="snow_and_ice_4tochki", stock=snow_and_ice_stock)
    # await populate_sheet(
    #     sheet="summer_4tochki", stock=stock_ordered_by_season["Летняя"]
    # )

    await message.reply(
        f"""Parsed JSON with keys: 
{', '.join([f'{key} ({len(value)})' for key, value in stock_ordered_by_season.items()])}"""
    )
