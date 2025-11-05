from typing import Any
import re

from gspread import Worksheet
from gspread.utils import ValueRenderOption
from pydantic import ValidationError, NonNegativeInt, model_validator, Field

from . import TireSKU, TireStock, VehicleType, SeasonType
from ..sheets import STC
from ..dicts.prefiltering import filter_new
from ..sheets.fresh_stock import prepare_table_data


LT_MAP = {
    "Легковая": VehicleType.LIGHT,
    "Мото": VehicleType.MOTORCYCLE,
    "Грузовая": VehicleType.TRUCK,
    "Спецтехника": VehicleType.SPECIAL,
}

SEAS_MAP = {
    "Зимняя": SeasonType.WINTER,
    "Летняя": SeasonType.SUMMER,
    "Всесезонная": SeasonType.ALLSEASON,
}


class Stock_4tochki(TireStock):
    art: str = ...
    amo_solonkl: NonNegativeInt = 0
    amo_kryarsk2: NonNegativeInt = 0

    @model_validator(mode="before")
    @classmethod
    def build_line(cls, line: dict[str, Any]):
        r_solonkl = (
            line.get("rest_oh_solonkl", 0)
            if line.get("rest_oh_solonkl", 0) != "более 40"
            else 40
        )
        r_kryarsk2 = (
            line.get("rest_kryarsk2", 0)
            if line.get("rest_kryarsk2", 0) != "более 40"
            else 40
        )

        return {
            "art": str(line.get("cae", None)),
            "price": line.get("price_kryarsk2", None),
            "amo_solonkl": r_solonkl,
            "amo_kryarsk2": r_kryarsk2,
        }


class SKU_4tochki(TireSKU):
    amo_solonkl: NonNegativeInt = 0
    amo_kryarsk2: NonNegativeInt = 0

    @model_validator(mode="before")
    @classmethod
    def build_line(cls, line: dict[str, Any]) -> dict[str, Any]:
        if line["diameter"]:
            d = re.sub(r"[^0-9.,]", "", line["diameter"])
            d = d.replace(",", ".")
        else:
            d = ""
        siz = f'{line.get("width", "")}{line.get("height", "")}{d}'
        raw_type = line.get("tiretype", None)
        if raw_type in LT_MAP:
            lt = LT_MAP[raw_type]

        seas = str(line.get("season", None))
        if seas in SEAS_MAP:
            seas = SEAS_MAP[seas]

        stud = True if line.get("thorn", None) else False
        name = f"{line.get('brand', '')} {line.get('model', '')}"
        full_size = (
            f"{line.get('width', '')}/{line.get('height', '')}{line.get('diameter', '')} "
            f"{line.get('load_index', '')}{line.get('speed_index', '')}"
        )
        #  Вычлинить full_size из line.get("name","")
        r_solonkl = (
            line.get("rest_oh_solonkl", 0)
            if line.get("rest_oh_solonkl", 0) != "более 40"
            else 40
        )
        r_kryarsk2 = (
            line.get("rest_kryarsk2", 0)
            if line.get("rest_kryarsk2", 0) != "более 40"
            else 40
        )

        return {
            "art": str(line["cae"]),
            "width": line.get("width", None),
            "hei": line.get("height", None),
            "diam": d,
            "siz": siz,
            "lt": lt,
            "seas": seas,
            "stud": stud,
            "supp": "4tochki",
            "name": name,
            "full_size": full_size,
            "amo_solonkl": r_solonkl,  # rest_oh_solonkl
            "amo_kryarsk2": r_kryarsk2,  # rest_kryarsk2
            "price": line.get("price_kryarsk2", None),
        }


async def harv_4tochki(data: dict[str, list[dict[str, Any]]], ws: Worksheet) -> None:

    new_data: list[dict[str, Any]] = []
    amo_data: list[dict[str, int | None]] = []

    unvalidated_lines: list[dict[str, Any]] = []
    no_amo_codes: list[dict[str, Any]] = []

    l: str = STC["4tochki"]["art"]["l"]
    col = f"{l}3:{l}"
    ex_arts: list[str] = {
        item[0] if item else ""
        for item in ws.get(col, value_render_option=ValueRenderOption.unformatted)
    }
    for obj in data["tires"]:
        if str(obj["cae"]) not in ex_arts:
            wanted_warehouses: tuple[str] = ("rest_kryarsk2", "rest_oh_solonkl")
            if any(k in obj for k in wanted_warehouses):
                try:
                    sku = SKU_4tochki.model_validate(obj)
                    new_data.append(sku.model_dump())
                except ValidationError:
                    unvalidated_lines.append(obj["name"])
        try:
            amo = Stock_4tochki.model_validate(obj)
            amo_data.append(amo.model_dump())
        except ValidationError:
            no_amo_codes.append(obj["cae"])

    return {
        "i_data": len(data["tires"]),
        "new_lines": new_data,
        "trash_lines": unvalidated_lines,
        "amo_data": amo_data,
        "no_amo_arts": no_amo_codes,
    }
