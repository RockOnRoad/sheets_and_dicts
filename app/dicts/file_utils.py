import json
import pandas as pd
from io import BytesIO
from typing import Any

from aiogram.types import Message, CallbackQuery, Document

from ..sheets import STC


# ---------- json ----------
async def load_json(file: BytesIO) -> dict:  # 4tochki: dict[str, list[dict[str, Any]]]
    """
    Parse JSON file from BytesIO.
    Caller is responsible for file.seek(0) before calling.
    """
    try:
        return json.load(file)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e


# ---------- excel ----------
async def load_excel(file: BytesIO) -> list[dict]:
    """
    Parse Excel file into list of dicts.
    Caller is responsible for file.seek(0) before calling.
    """
    try:
        df = pd.read_excel(file)
        return df.to_dict(orient="records")
    except Exception as e:
        raise ValueError(f"Invalid Excel file: {e}") from e


# ---------- csv ----------
async def load_csv(file: BytesIO) -> list[dict]:
    """
    Parse CSV into list of dicts.
    Caller is responsible for file.seek(0) before calling.
    """
    try:
        df = pd.read_csv(file)
        return df.to_dict(orient="records")
    except Exception as e:
        raise ValueError(f"Invalid CSV file: {e}") from e


# ---------- MAIN ----------


async def file_to_dict(msg: Message, supplier: str) -> None:
    """**Processes the uploaded file based on the supplier**.

    :param message: The message containing the file to process.
    :param supplier: The supplier name to determine how to process the file.
    :return: Parsed data from the file, or None if processing failed.
    """
    doc: Document = msg.document

    file = BytesIO()
    await msg.bot.download(doc.file_id, destination=file)
    file.seek(0)

    name = doc.file_name.lower()
    mime = doc.mime_type

    try:
        if supplier == list(STC)[2]:
            if name.endswith(".json") or mime == "application/json":
                data = await load_json(file)  # 4tochki: dict[str, list[dict[str, Any]]]
            else:
                await msg.reply("Файл не поддерживается (нужен JSON).")
                #  Переделать чтобы на callback отвечал через edit_text
                return
        elif supplier in list(STC)[3:]:
            if name.endswith((".xls", ".xlsx")) or "excel" in mime:
                data = await load_excel(file)
            else:
                await msg.reply("Файл не поддерживается (нужен Excel).")
                return
        else:
            await msg.reply("Неизвестный поставщик.")
            return
    except ValueError as e:
        await msg.reply(str(e))
        return
    finally:
        file.close()

    return data
