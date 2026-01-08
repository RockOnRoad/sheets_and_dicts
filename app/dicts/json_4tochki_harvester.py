from typing import Any
import re

from gspread import Worksheet
from gspread.utils import ValueRenderOption
import pandas as pd
from pandas import DataFrame
from pydantic import ValidationError, NonNegativeInt, model_validator

from . import TireSKU, TireStock, VehicleType, SeasonType
from ..sheets import STC


class Stock_4tochki(TireStock):
    art: str = ...
    amo_solonkl: NonNegativeInt = 0
    amo_kryarsk2: NonNegativeInt = 0

    @model_validator(mode="before")
    @classmethod
    def build_line(cls, line: dict[str, Any]):

        r_solonkl = line.get("rest_oh_solonkl", 0)
        r_solonkl = (
            40 if r_solonkl == "более 40" else (0 if pd.isna(r_solonkl) else r_solonkl)
        )

        r_krk2 = line.get("rest_kryarsk2", 0)
        r_krk2 = 40 if r_krk2 == "более 40" else (0 if pd.isna(r_krk2) else r_krk2)

        price = line.get("price_kryarsk2", 0)
        price = None if pd.isna(price) else price

        return {
            "art": line.get("art", None),
            "price": price,
            "amo_solonkl": r_solonkl,
            "amo_kryarsk2": r_krk2,
        }


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


class SKU_4tochki(TireSKU):

    @model_validator(mode="before")
    @classmethod
    def build_line(cls, obj: dict[str, Any]) -> dict[str, Any]:

        w = obj.get("width", "")
        width = int(w) if w.is_integer() else w

        d = re.sub(r"[^0-9.,]", "", obj.get("diam", ""))
        d = d.replace(",", ".")
        siz = f"{width}{obj.get("hei", "")}{d}"
        lt = LT_MAP.get(obj["lt"], None)

        seas = SEAS_MAP.get(obj["seas"], None)

        stud = True if obj.get("stud", None) else False

        side = f" {obj["side"]}" if obj.get("side", None) else ""
        name = f"{obj.get('brand', '')} {obj.get('model', '')}{side}"

        xl = " XL" if obj.get("xl", None) else ""
        full_size = (
            f"{width}/{obj.get('hei', '')}{obj.get('diam', '')} "
            f"{obj.get('load_index', '')}{obj.get('speed_index', '')}{xl}"
        )

        return {
            "art": obj["art"],
            "width": width,
            "hei": obj.get("hei", ""),
            "diam": d,
            "siz": siz,
            "lt": lt,
            "seas": seas,
            "stud": stud,
            "supp": "4tochki",
            "name": name,
            "full_size": full_size,
            "local_art": "",
            "text": obj.get("naming"),
        }


async def harv_4tochki(data: DataFrame, ws: Worksheet) -> None:

    validated_data = {
        "i_data": 0,  # int
        "new_lines": [],  # list[dict[str, Any]]
        "amo_data": [],  # list[dict[str, int | None]]
        "trash_lines": [],  # list[dict[str, Any]]
        "no_amo_arts": [],  # list[dict[str, Any]]
    }

    df: DataFrame = data[
        [
            "cae",
            "rest_oh_solonkl",
            "price_kryarsk2",
            "rest_kryarsk2",
            "brand",
            "model",
            "width",
            "height",
            "diameter",
            "tonnage",  # XL
            "load_index",
            "speed_index",
            "season",
            "thorn",  # Шипы
            "tiretype",
            "side",
            "usa",
            "name",
        ]
    ]

    instock_df = df[df["rest_oh_solonkl"].notna() | df["price_kryarsk2"].notna()]

    _l: str = STC["4tochki"]["art"]["l"]
    col = f"{_l}3:{_l}"
    ex_arts: list[str] = {
        item[0] if item else ""
        for item in ws.get(col, value_render_option=ValueRenderOption.unformatted)
    }

    new_df: DataFrame = instock_df[~instock_df["cae"].isin(ex_arts)]

    new_SKUs = new_df.to_dict(orient="records")
    validated_data["i_data"] = len(new_SKUs)
    for obj in new_SKUs:
        try:
            sku_object = {
                "art": str(obj["cae"]),
                "brand": obj["brand"],
                "model": obj["model"],
                "width": obj["width"],
                "hei": obj["height"],
                "diam": obj["diameter"],
                "load_index": obj["load_index"],
                "speed_index": obj["speed_index"],
                "xl": obj["tonnage"],
                "lt": obj["tiretype"],
                "seas": obj["season"],
                "stud": obj["thorn"],
                "side": obj["side"],
                "usa": obj["usa"],
                "naming": obj["name"],
            }
            sku_validated = SKU_4tochki.model_validate(sku_object)
            validated_data["new_lines"].append(sku_validated.model_dump())
        except ValidationError as e:
            validated_data["trash_lines"].append(
                {"name": obj["name"], "val_error": str(e)}
            )

    amo_df: DataFrame = instock_df[
        [
            "cae",
            "rest_oh_solonkl",
            "rest_kryarsk2",
            "price_kryarsk2",
        ]
    ]
    amounts = amo_df.to_dict(orient="records")
    for obj in amounts:
        try:
            amo_object = {
                "art": str(obj["cae"]),
                "rest_oh_solonkl": obj["rest_oh_solonkl"],
                "rest_kryarsk2": obj["rest_kryarsk2"],
                "price_kryarsk2": obj["price_kryarsk2"],
            }
            amo_validated = Stock_4tochki.model_validate(amo_object)
            validated_data["amo_data"].append(amo_validated.model_dump())
        except ValidationError as e:
            validated_data["no_amo_arts"].append(
                {"name": obj["cae"], "val_error": str(e)}
            )
            print(f"{obj["cae"]}\n{e}\n\n")

    # df = instock_df[["width", "height", "diameter", "load_index", "speed_index"]]
    # df_d = df.to_dict(orient="records")
    # for i in enumerate(df_d):
    #     print(f"{i}")
    return validated_data
