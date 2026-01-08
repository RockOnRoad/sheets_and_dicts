import asyncio
import json
import pandas as pd
from pandas import ExcelFile, json_normalize
from io import BytesIO
from typing import Any

from aiogram.types import Message, Document
from gspread import Worksheet

from app.sheets import STC
from app.dicts.json_4tochki_harvester import harv_4tochki
from app.dicts.xls_olta_harvester import harv_olta
from app.dicts.xlsx_ShinaTorg_harvester import harv_shina_torg
from app.dicts.xlsx_BigMachine_harvester import harv_big_machine
from app.dicts.xlsx_Simoshkevich_harvester import harv_simoshkevich
from app.dicts.xlsx_Scotchenko_harvester import harv_scotchenko


async def file_handler(msg: Message, supplier: str, ws: Worksheet):
    doc: Document = msg.document

    validated_data: dict = {}

    with BytesIO() as file:
        await msg.bot.download(doc.file_id, destination=file)
        file.seek(0)

        name = doc.file_name.lower()
        mime = doc.mime_type

        data: Any = None

        try:
            if name.endswith(".json") or mime == "application/json":
                if supplier == list(STC)[2]:  # 4tochki
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError as e:
                        raise ValueError(f"Invalid JSON: {e}") from e
                    df = pd.DataFrame(data["tires"])
                    # df = json_normalize(data["tires"])
                    validated_data = await harv_4tochki(data=df, ws=ws)
                else:
                    await msg.reply(f"<b>.json</b> Поставщик {supplier} не найден")
                    return

            elif name.endswith((".xls", ".xlsx")) or "excel" in mime:
                # df = pd.read_excel(file)
                # data: dict = df.to_dict(orient="records")
                data: ExcelFile = pd.ExcelFile(file)
                if supplier == list(STC)[3]:  # olta
                    validated_data = await harv_olta(xlsx=data, ws=ws)
                elif supplier == list(STC)[4]:  # shina_torg
                    validated_data = await harv_shina_torg(xlsx=data, ws=ws)
                elif supplier == list(STC)[5]:  # big_mashina
                    validated_data = await harv_big_machine(xlsx=data, ws=ws)
                elif supplier == list(STC)[6]:  # simoshkevich
                    validated_data = await harv_simoshkevich(xlsx=data, ws=ws)
                # elif supplier == list(STC)[7]:  # scotchenko
                #     validated_data = await harv_scotchenko(xlsx=data, ws=ws)
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
