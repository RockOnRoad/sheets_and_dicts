import json
from random import randint

from io import BytesIO
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, Document
# from gspread import Worksheet
import pandas as pd

from app.dicts.convert import divide_by_key, remove_unnecessary_keys, olta_xls_pretty, olta_xls_sort
from app.sheets.add_amounts import update_amounts
from app.sheets.add_rows import append_rows
from app.sheets.olta_populate import add_rows
from app.sheets import sheets_conn


rtr = Router()


@rtr.message(F.document.file_name.endswith(".json"))
async def handle_json_file(message: Message) -> None:
    """Отлавливает json файлы, парсит их содержимое и добавляет это содержимое в таблицу."""

    key: str = "season"

    if not message.document.file_name.endswith(".json"):
        await message.reply("Только .json файлы поддерживаются.")
        return

    file_obj = BytesIO()
    await message.bot.download(message.document.file_id, destination=file_obj)
    file_obj.seek(0)

    try:
        data = json.load(file_obj)
    except Exception as e:
        file_obj.close()
        await message.reply(f"Ошибка при обработке файла: {str(e)}")
        return
    else:
        await message.answer(
            f"Файл <b>{message.document.file_name}</b> успешно загружен."
        )
        file_obj.close()

    only_tires: list = data["tires"]
    await message.answer(
        f"✅ Файл прочитан.\nКоличество позиций шин: <b>{len(only_tires)}</b>"
    )

    only_kryarsk2: list = [line for line in only_tires if "price_kryarsk2" in line]
    #  [{'cae': 'F7640', 'gtin': 02900077764912, 'name': '...'}, {'cae': 'F7641', 'a': 3, 'b': 4}, ...]
    await message.answer(
        f"✅ Количество позиций шин в наличии на складе Красноярск2: <b>{len(only_kryarsk2)}</b>"
    )

    clean_dicts: list = await remove_unnecessary_keys(only_kryarsk2)
    #  [{'cae': 'F7640', 'name': '...'}, {'cae': 'F7641', ...}, ...]

    separorated_stock: dict = await divide_by_key(data=clean_dicts, param=key)
    #  {'Зимняя': [{'cae': 'F7640', 'name': ...}, {}, {}], 'Летняя': [{'cae': '2177000', {}, {}], ...}

    await message.answer(
        f"""✅ Позиции рассортированы по сезону.
{'\n'.join([f'{key} ({len(value)} строк)' for key, value in separorated_stock.items()])}"""
    )

    if key == "season":

        sheets = {
            # "Зимняя": "test"
            "Зимняя": "snow_4tochki",
            "Летняя": "summer_4tochki",
            "Всесезонная": "all_season_4tochki",
        }

        for item in sheets:
            ws = await sheets_conn(sheets[item])

            await append_rows(sheet=ws, stock=separorated_stock[item], message=message)
            await message.answer(
                f"✅ Новые позиции добавлены в конец таблицы <b>{sheets[item]}</b>."
            )

            await update_amounts(sheet=ws, stock=clean_dicts, message=message)


@rtr.message(F.document.file_name.endswith(".xls"))
async def handle_xls_file(message: Message) -> None:
    file_info = await message.bot.get_file(message.document.file_id)
    downloaded_file = await message.bot.download_file(file_info.file_path)
    with downloaded_file:
        olta: list[dict] = pd.read_excel(downloaded_file).to_dict(orient="records")
        # [{'Код': '***', 'Артикул ': nan, ...}, {... , 'Номенклатура': 'автошина 145/65 R15 YOKOHAMA IG60 72Q', ...}]

    olta_dict: list[dict] = await olta_xls_pretty(data=olta, pd=pd)

    ws = await sheets_conn("olta_test")
    await add_rows(data=olta_dict, sheet=ws)

    # print(olta_dict[4540:4550])
    print(len(olta_dict))
    # for i in range(20):
    #     li = randint(0, len(olta_dict))
    #     print(f"{li}\n{olta_dict[li]}")



@rtr.message(F.document)
async def wrong_format(message: Message) -> None:
    await message.answer(
        "Допускаются только файлы форматов:\n`.json` для 4tochki\n`.xls` для olta"
    )
