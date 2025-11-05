import asyncio
import json
import pandas as pd
from pandas import ExcelFile
from io import BytesIO
from typing import Any

from aiogram.types import Message, Document
from gspread import Worksheet

from app.sheets import STC
from app.dicts.json_4tochki_harvester import harv_4tochki
from app.dicts.xls_olta_harvester import harv_olta
from app.dicts.xlsx_ShinaTorg_harvester import harv_shina_torg
from app.dicts.xlsx_BigMachine_harvester import harv_big_machine
from app.dicts.xlsx_Simash_harvester import harv_simash


async def file_handler(msg: Message, supplier: str, ws: Worksheet):
    doc: Document = msg.document

    validated_data: dict = {}

    with BytesIO() as file:
        await msg.bot.download(doc.file_id, destination=file)
        file.seek(0)

        name = doc.file_name.lower()
        mime = doc.mime_type

        data: Any = None
        print("File loop started")

        try:
            if name.endswith(".json") or mime == "application/json":
                if supplier == list(STC)[2]:  # 4tochki
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError as e:
                        raise ValueError(f"Invalid JSON: {e}") from e
                    validated_data = await harv_4tochki(data=data, ws=ws)
                else:
                    await msg.reply(f"<b>.json</b> Поставщик {supplier} не найден")
                    return

            elif name.endswith((".xls", ".xlsx")) or "excel" in mime:
                print("Excel detected")
                if supplier == list(STC)[3]:  # olta
                    #  fix: Тоже возвращать pd.ExcelFile
                    df = pd.read_excel(file)
                    data: dict = df.to_dict(orient="records")
                    validated_data: list[dict[str, Any]] = await harv_olta(
                        data=data, ws=ws
                    )
                elif supplier == list(STC)[4]:  # shina_torg
                    #  fix: Тоже возвращать pd.ExcelFile
                    df = pd.read_excel(file)
                    data: dict = df.to_dict(orient="records")
                    validated_data: list[dict[str, Any]] = await harv_shina_torg(
                        raw_data=data, ws=ws
                    )
                elif supplier == list(STC)[5]:  # big_mashina
                    data: ExcelFile = pd.ExcelFile(file)
                    validated_data = await harv_big_machine(xlsx=data, ws=ws)
                elif supplier == list(STC)[6]:  # simash
                    data: ExcelFile = pd.ExcelFile(file)
                    validated_data = await harv_simash(xlsx=data, ws=ws)
                    print(validated_data["i_data"])
                    print(len(validated_data["amo_data"]))
                else:
                    await msg.reply(f"<b>excel</b> Поставщик {supplier} не найден")
                    raise ValueError(f"<b>excel</b> Поставщик {supplier} не найден")
            else:
                await msg.reply("Файл не поддерживается (нужен Excel или JSON).")
                return

        except ValueError as e:
            await msg.reply(str(e))
            return

    return validated_data
