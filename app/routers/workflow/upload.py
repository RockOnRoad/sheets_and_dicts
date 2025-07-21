import json
from io import BytesIO
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from gspread import Worksheet

from app.dicts.convert import order_and_upload, remove_unnecessary_keys
from app.sheets.add_amounts import update_amounts
from app.sheets import sheets_conn


rtr = Router()


@rtr.message(F.document)
async def handle_json_file(message: Message):
    sheet: str = "test"
    ws: Worksheet = await sheets_conn(sheet)

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

    await order_and_upload(
        parameter="season", data=clean_dicts, sheet=ws, message=message
    )
    await message.answer("✅ Новые позиции добавлены в конец таблицы.")

    await update_amounts(sheet=ws, stock=clean_dicts, message=message)
