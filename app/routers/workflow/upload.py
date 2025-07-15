import json
from io import BytesIO
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery


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

    await message.reply(f"Parsed JSON with keys: {', '.join(data.keys())}")
