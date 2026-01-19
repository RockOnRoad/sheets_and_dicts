from typing import Any

from gspread import Worksheet
from gspread.utils import ValueRenderOption
import pandas as pd
from pandas import ExcelFile, DataFrame
from pydantic import ValidationError, NonNegativeInt, model_validator

from app.dicts import TireSKU, TireStock, SeasonType, VehicleType
from app.sheets import STC
from app.sheets.parse_supplier_naming import parse_all


class Stock_Simoshkevich(TireStock):
    local_art: str = ...
    amo: NonNegativeInt = 0

    @model_validator(mode="before")
    @classmethod
    def _build_line(cls, obj: dict[str, Any]):
        amo: int = 0
        try:
            amo = int(obj["amo"])
        except (ValueError, TypeError):
            amo = 12

        return {
            "local_art": obj.get("local_art", ""),
            "price": obj.get("price", None),
            "amo": amo,
        }


class SKU_Simoshkevich(TireSKU):
    local_art: str = ...
    age: str | None = None
    text: str = ""

    @model_validator(mode="before")
    @classmethod
    def _build_line(cls, obj: dict[str, Any]):

        parsed_obj: dict[str, Any] = parse_all(text=obj["naming"].upper())

        siz: str = f"{parsed_obj['width']}{parsed_obj['height']}{parsed_obj['diam']}"
        name: str = f"{parsed_obj['brand']} {parsed_obj['model']}{parsed_obj['suv']}"
        full_size: str = (
            f"{parsed_obj['width']}/{parsed_obj['height']}{parsed_obj['diameter']}"
            f" {parsed_obj['indexes']}{parsed_obj['xl']}"
        )

        return {
            "art": obj["art"],
            "width": parsed_obj["width"],
            "hei": parsed_obj["height"],
            "diam": parsed_obj["diam"],
            "siz": siz,
            "lt": obj["lt"],
            "seas": obj["seas"],
            "stud": parsed_obj["stud"],
            "age": parsed_obj["year"],
            "supp": "simoshkevich",
            "name": name,
            "full_size": full_size,
            "local_art": obj["local_art"],
            "text": obj["naming"],
        }


async def harv_simoshkevich(xlsx: ExcelFile, ws: Worksheet) -> None:
    #  Добавить страну производителя в таблицу

    df: DataFrame = pd.read_excel(xlsx, xlsx.sheet_names[0])

    _l: str = STC["simoshkevich"]["local_art"]["l"]
    ex_local_arts: set[str] = {
        item[0] if item else ""
        for item in ws.get(
            f"{_l}3:{_l}", value_render_option=ValueRenderOption.unformatted
        )
    }

    df: DataFrame = df[df[df.columns[10]].notna()]

    df_striped: DataFrame = df[
        [
            df.columns[0],  # art
            df.columns[5],  # local_art
            df.columns[10],  # naming
            df.columns[14],  # price
            df.columns[15],  # amo
            df.columns[16],  # brand_discount
        ]
    ]
    df_striped.columns = [
        "art",
        "local_art",
        "naming",
        "price",
        "amo",
        "brand_discount",
    ]
    df_new: DataFrame = df_striped[~df_striped["local_art"].isin(ex_local_arts)]

    # pd.set_option("display.max_columns", None)
    # print(df_striped.head(10))

    new_data: list[dict[str, Any]] = df_new.to_dict(orient="records")
    seas: str = None  # None, w, s
    lt: str = None  # None, l, lt

    validated_data = {
        "i_data": 0,  # int
        "new_lines": [],  # list[dict[str, Any]]
        "amo_data": [],  # list[dict[str, int | None]]
        "trash_lines": [],  # list[dict[str, Any]]
        "no_amo_arts": [],  # list[dict[str, Any]]
    }

    for obj in new_data:
        if "номенклатура" in obj["naming"].lower():
            continue

        if "зимние" in obj["naming"].lower():
            seas = SeasonType.WINTER
            lt = VehicleType.LIGHT
            continue
        elif "летние" in obj["naming"].lower():
            seas = SeasonType.SUMMER
            lt = VehicleType.LIGHT
            continue
        elif "всесезонные" in obj["naming"].lower():
            seas = SeasonType.ALLSEASON
            lt = VehicleType.LIGHT
            continue
        elif "легкогрузовые" in obj["naming"].lower():
            seas = SeasonType.WINTER
            lt = VehicleType.LIGHTTRUCK
            continue
        elif "грузовые" in obj["naming"].lower():
            break

        validated_data["i_data"] += 1

        try:
            sku_object = {
                "art": str(obj["art"]),
                "local_art": str(obj["local_art"]),
                "naming": str(obj["naming"]),
                "brand_discount": str(obj["brand_discount"]),
                "lt": lt,
                "seas": seas,
            }
            sku_validated = SKU_Simoshkevich.model_validate(sku_object)
            validated_data["new_lines"].append(sku_validated.model_dump())
        except ValidationError as e:
            validated_data["trash_lines"].append(
                {"name": str(obj["naming"]), "val_error": str(e)}
            )

    df_amounts: DataFrame = df[[df.columns[5], df.columns[14], df.columns[15]]]
    df_amounts.columns = ["local_art", "price", "amo"]
    df_amounts: DataFrame = df_amounts[df_amounts["amo"].notna()]
    amounts: list[dict[str, Any]] = df_amounts.to_dict(orient="records")
    # {'local_art': 'Из079', 'price': 4700, 'amo': 3}

    for amo_obj in amounts:
        try:
            amo_object = {
                "local_art": str(amo_obj["local_art"]),
                "price": amo_obj["price"],
                "amo": amo_obj["amo"],
            }
            amo_validated = Stock_Simoshkevich.model_validate(amo_object)
            validated_data["amo_data"].append(amo_validated.model_dump())
        except ValidationError as e:
            validated_data["no_amo_arts"].append(
                {"name": amo_object["local_art"], "val_error": str(e)}
            )
            # print(f"{type(amo_object["price"])} - {amo_object["price"]}: {e}\n\n")
    return validated_data
