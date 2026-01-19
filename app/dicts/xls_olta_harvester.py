import re
from typing import Any

# from math import isnan
from gspread import Worksheet
from gspread.utils import ValueRenderOption
import pandas as pd  # type: ignore
from pandas import ExcelFile, DataFrame
from pydantic import ValidationError, NonNegativeInt, model_validator

from . import TireSKU, TireStock, VehicleType, SeasonType
from ..sheets import STC
from app.sheets.parse_supplier_naming import parse_stud


class StockOlta(TireStock):
    local_art: str = ...
    amo: NonNegativeInt = 0

    @model_validator(mode="before")
    @classmethod
    def _build_line(cls, line: dict[str, Any]):
        # amo = line.get("Красноярск", 0) if isinstance(line["Красноярск"], int) else 20
        amo: int = 0
        try:
            amo = int(line["amo"])
        except (ValueError, TypeError):
            amo = 20

        return {
            "local_art": line.get("local_art", ""),
            "price": line.get("price", None),
            "amo": amo,
        }


class SKU_Olta(TireSKU):
    local_art: str = ...
    age: str | None = None

    @model_validator(mode="before")
    @classmethod
    def _build_line(cls, obj: dict[str, Any]):

        parsed_obj: dict[str, Any] = parse_stud(text=obj["naming"].upper(), seq=True)

        siz: str = f"{parsed_obj['width']}{parsed_obj['height']}{parsed_obj['diam']}"
        name: str = f"{parsed_obj['brand']} {parsed_obj['model']}{parsed_obj['suv']}"

        h = f"/{parsed_obj['height']}" if parsed_obj["height"] else ""
        full_size: str = (
            f"{parsed_obj['width']}{h}{parsed_obj['diameter']}"
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
            "supp": "olta",
            "name": name,
            "full_size": full_size,
            "local_art": obj["local_art"],
            "text": obj["naming"],
        }


async def harv_olta(xlsx: ExcelFile, ws: Worksheet):

    #  Конвертируем единственный лист в DataFrame
    df: DataFrame = pd.read_excel(xlsx, xlsx.sheet_names[0])

    #  Leaving only necessary columns
    df = df.iloc[:, [1, 2, 3, 4, 5, 9]]
    #  Naming those necessary columns
    df.columns = ["art", "naming", "age", "local_art", "amo", "price"]

    _l: str = STC["olta"]["local_art"]["l"]

    ex_local_arts: list[str] = {
        item[0] if item else ""
        for item in ws.get(
            f"{_l}3:{_l}", value_render_option=ValueRenderOption.unformatted
        )
    }

    validated_data = {
        "i_data": 0,  # int
        "new_lines": [],  # list[dict[str, Any]]
        "amo_data": [],  # list[dict[str, int | None]]
        "trash_lines": [],  # list[dict[str, Any]]
        "no_amo_arts": [],  # list[dict[str, Any]]
    }

    #  New SKUs, no rubish
    df_new: DataFrame = df.loc[
        df["naming"].notna() & ~df["local_art"].isin(ex_local_arts), df.columns[0:5]
    ]
    new_SKUs: dict = df_new.to_dict(orient="records")
    seas: str = None  # None, w, s
    lt: str = None  # None, l, lt

    for obj in new_SKUs:
        if "ШИНЫ" in obj["naming"].upper():
            continue

        if "ЗИМНИЕ" in obj["naming"].upper():
            seas = SeasonType.WINTER
            continue
        elif "ЛЕТНИЕ" in obj["naming"].upper():
            seas = SeasonType.SUMMER
            continue
        elif "ВСЕСЕЗОННЫЕ" in obj["naming"].upper():
            seas = SeasonType.ALLSEASON
            continue

        if "ЛЕГКОВЫЕ" in obj["naming"].upper():
            lt = VehicleType.LIGHT
            continue
        elif "ЛЕГКОГРУЗОВЫЕ" in obj["naming"].upper():
            lt = VehicleType.LIGHTTRUCK
            continue
        elif "ГРУЗОВЫЕ" in obj["naming"].upper():
            break

        # if pd.notna(obj["local_art"]):
        if pd.notna(obj["local_art"]) and pd.notna(obj["amo"]):

            validated_data["i_data"] += 1

            try:
                sku_object = {
                    "art": str(obj["art"]),
                    "local_art": str(obj["local_art"]),
                    "naming": str(obj["naming"]),
                    "age": str(obj["age"]),
                    "lt": lt,
                    "seas": seas,
                }
                sku_validated = SKU_Olta.model_validate(sku_object)
                validated_data["new_lines"].append(sku_validated.model_dump())
            except ValidationError as e:
                validated_data["trash_lines"].append(
                    {"name": str(obj["naming"]), "val_error": str(e)}
                )
                # print(f"{str(obj["naming"])}\n{e}\n\n")

    df_amo: DataFrame = df.loc[df["amo"].notna() & df["price"].notna(), df.columns[3:6]]
    amounts: list[dict] = df_amo.to_dict(orient="records")
    # pd.set_option("display.max_columns", None)
    # print(df_amo.columns)
    # print(df_amo.head(60))

    for amo_obj in amounts:
        try:
            amo_object = {
                "local_art": str(amo_obj["local_art"]),
                "price": amo_obj["price"],
                "amo": amo_obj["amo"],
            }
            amo_validated = StockOlta.model_validate(amo_object)
            validated_data["amo_data"].append(amo_validated.model_dump())
        except ValidationError as e:
            validated_data["no_amo_arts"].append(
                {"name": amo_object["local_art"], "val_error": str(e)}
            )
            print(f"{type(amo_object["price"])} - {amo_object["price"]}\n{e}\n\n")
    return validated_data
