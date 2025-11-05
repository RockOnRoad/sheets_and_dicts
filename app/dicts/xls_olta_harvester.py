import re
from typing import Any

# from math import isnan
from gspread import Worksheet
from gspread.utils import ValueRenderOption
import pandas as pd  # type: ignore
from pydantic import ValidationError, NonNegativeInt, model_validator

from . import TireSKU, TireStock, VehicleType, SeasonType
from ..sheets import STC


class StockOlta(TireStock):
    code_w_prefix: str = ...
    amo: NonNegativeInt = 0

    @model_validator(mode="before")
    @classmethod
    def _build_line(cls, line: dict[str, Any]):

        amo = line.get("Красноярск", 0) if isinstance(line["Красноярск"], int) else 20
        return {
            "code_w_prefix": line.get("Код с префиксом", ""),
            "price": line.get("Цена с основного склада в отсрочку", None),
            "amo": amo,
        }


class SKU_olta(TireSKU):
    code_w_prefix: str = ...
    age: str | None = None
    # amo: NonNegativeInt = 0

    @model_validator(mode="before")
    @classmethod
    def _build_line(cls, line: dict[str, Any]):
        pattern = re.compile(
            r"\s+"
            r"(?:"
            r"(?:(?P<width>\d{1,3})[x/]?)?"
            r"(?:(?P<height>\d{1,2}(?:[,.]\d{1,2})?))?"
            r"\s*(?P<diameter>(?:(?:RZ|Z)?R)\d{2}(?:[,.]\d)?[CС]?)"
            r")\s+"
            r"(?P<brand>[^\s]+)\s+"
            r"(?P<model>.+?)\s+"
            r"(?P<indexes>\d{2,3}(?:/\d{2,3})?(?:[A-ZТ]|ZR))"
            r"(?:\s+(?P<xl>XL)(?=\s|$))?"
            r"(?:\s+(?P<stud>Ш)(?=\s|$))?"
            r"(?:\s+(?P<suv>SUV)(?=\s|$))?"
        )

        m = pattern.search(line["naming"])
        params = {}
        if m:
            params = m.groupdict()

        try:
            width = params.get("width", "").replace(",", ".")
            width = float(width) if "." in width else int(width)
        except (ValueError, AttributeError):
            width = ""

        try:
            hei = params.get("height", "").replace(",", ".")
            hei = float(hei) if "." in hei else int(hei)
        except (ValueError, AttributeError):
            hei = ""

        diameter = params.get("diameter", "")
        diam = re.sub(r"[^0-9.,]", "", diameter)
        diam = diam.replace(",", ".")

        if {params.get("height", None)}:
            size = (
                f"{params.get("width", "")}/{params.get("height", "")} {str(diameter)}"
            )
        else:
            size = f"{params.get("width", "")}{str(diameter)}"

        name = f'{params.get("brand", "")}_{params.get("model", "")}'.strip()
        name = " ".join(part.capitalize() for part in name.split("_"))

        age = None if isinstance(line["age"], float) else str(line.get("age", ""))

        amo = line.get("amo", 0) if isinstance(line["amo"], int) else 20

        return {
            "art": line.get("art", None),
            "code_w_prefix": line.get("code_w_prefix", ""),
            "width": width,
            "hei": hei,
            "diam": diam,
            "siz": f'{params.get("width", "")}{params.get("height", "")}{diam}',
            "lt": line.get("lt", None),
            "seas": line.get("seas", None),
            "stud": True if params.get("stud", None) == "Ш" else False,
            "supp": "olta",
            "name": name,
            "full_size": f"{size} {params.get("indexes", "")}{' XL' if params.get('xl', None) else ''}",
            "age": age,
            "price": line.get("price", None),
            "amo": amo,
        }


async def harv_olta(data: list[dict[str, Any]], ws: Worksheet) -> list[dict[str, Any]]:
    new_data: list[dict[str, Any]] = []
    amo_data: list[dict[str, int | None]] = []

    unvalidated_lines: list[dict[str, Any]] = []
    no_amo_codes: list[dict[str, Any]] = []

    seas: str = None  # None, w, s
    lt: str = None  # None, l, lt

    _l: str = STC["olta"]["code_w_prefix"]["l"]
    ex_arts: list[str] = {
        item[0] if item else ""
        for item in ws.get(
            f"{_l}3:{_l}", value_render_option=ValueRenderOption.unformatted
        )
    }

    for obj in data:
        if pd.notna(obj["Номенклатура"]):
            if "ЗИМНИЕ" in obj["Номенклатура"]:
                seas = SeasonType.WINTER
                continue
            elif "ЛЕТНИЕ" in obj["Номенклатура"]:
                seas = SeasonType.SUMMER
                continue
            elif "ВСЕСЕЗОННЫЕ" in obj["Номенклатура"]:
                seas = SeasonType.ALLSEASON
                continue

            if "ЛЕГКОВЫЕ" in obj["Номенклатура"]:
                lt = VehicleType.LIGHT
                continue
            elif "ЛЕГКОГРУЗОВЫЕ" in obj["Номенклатура"]:
                lt = VehicleType.LIGHTTRUCK
                continue
            elif "ГРУЗОВЫЕ" in obj["Номенклатура"]:
                break

            if pd.notna(obj["Красноярск"]):
                if obj["Код с префиксом"] not in ex_arts:
                    new_obj = {
                        "art": str(obj["Артикул "]),
                        "code_w_prefix": obj["Код с префиксом"],
                        "age": obj.get("Харктеристика номенклатуры", None),
                        "naming": str(obj["Номенклатура"]),
                        "lt": lt,
                        "seas": seas,
                        "amo": obj["Красноярск"],
                        "price": obj["Цена с основного склада в отсрочку"],
                    }
                    try:
                        sku = SKU_olta.model_validate(new_obj)
                        new_data.append(sku.model_dump())
                    except ValidationError:
                        unvalidated_lines.append(obj["Номенклатура"])

                try:
                    amo = StockOlta.model_validate(obj)
                    amo_data.append(amo.model_dump())
                except ValidationError:
                    no_amo_codes.append(obj["Код с префиксом"])

    # print(unvalidated_lines)
    return {
        "i_data": len(data),
        "new_lines": new_data,
        "trash_lines": unvalidated_lines,
        "amo_data": amo_data,
        "no_amo_arts": no_amo_codes,
    }
