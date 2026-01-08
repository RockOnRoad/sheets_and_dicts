import re
from typing import Any

from gspread import Worksheet
from gspread.utils import ValueRenderOption
import pandas as pd
from pandas import ExcelFile, DataFrame
from pydantic import ValidationError, NonNegativeInt, model_validator

from app.dicts import TireSKU, TireStock, SeasonType, VehicleType
from app.sheets import STC
from app.sheets.parse_supplier_naming import parse_all


class Stock_ShinaTorg(TireStock):
    art: str = ...
    amo: NonNegativeInt = 0

    @model_validator(mode="before")
    @classmethod
    def _build_line(cls, line: dict[str, Any]):

        amo = line.get("amo", 0) if isinstance(line["amo"], int) else 50
        return {
            "art": str(line.get("art", "")),
            "price": line.get("price", None),
            "amo": amo,
        }


class SKU_ShinaTorg(TireSKU):
    age: str | None = None

    @model_validator(mode="before")
    @classmethod
    def _build_line(cls, obj: dict[str, Any]):

        parsed_obj: dict[str, Any] = parse_all(text=obj["naming"].upper())

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
            "age": parsed_obj["year"],
            "supp": "shina_torg",
            "name": name,
            "full_size": full_size,
            "text": obj["naming"],
        }


async def harv_shina_torg(xlsx: ExcelFile, ws: Worksheet) -> None:
    df: DataFrame = pd.read_excel(xlsx, xlsx.sheet_names[0])

    #  Leaving only necessary columns
    df: DataFrame = df.iloc[:, [0, 1, 3, 2]]
    #  Naming those necessary columns
    df.columns = ["art", "naming", "amo", "price"]

    _l: str = STC["shina_torg"]["art"]["l"]
    ex_arts: list[str] = {
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

    #  New SKUs, columns art, naming, amo
    df_new: DataFrame = df.loc[
        df["naming"].notna() & ~df["art"].isin(ex_arts), df.columns[0:3]
    ]
    new_SKUs: dict = df_new.to_dict(orient="records")

    seas: str = None  # None, w, s
    lt: str = None  # None, l, lt
    for obj in new_SKUs:
        if "зима" in obj["naming"].lower():
            seas = SeasonType.WINTER
        elif "лето" in obj["naming"].lower():
            seas = SeasonType.SUMMER
        elif "всесезонные" in obj["naming"].lower():
            seas = SeasonType.ALLSEASON

        if "легковые" in obj["naming"].lower():
            lt = VehicleType.LIGHT
            continue
        elif "легкогрузовые" in obj["naming"].lower():
            lt = VehicleType.LIGHTTRUCK
            continue
        elif "грузовые" in obj["naming"].lower():
            break

        if pd.notna(obj["art"]) and pd.notna(obj["amo"]):

            validated_data["i_data"] += 1

            try:
                sku_object = {
                    "art": str(obj["art"]),
                    "naming": str(obj["naming"]),
                    "lt": lt,
                    "seas": seas,
                }
                sku_validated = SKU_ShinaTorg.model_validate(sku_object)
                validated_data["new_lines"].append(sku_validated.model_dump())
            except ValidationError as e:
                validated_data["trash_lines"].append(
                    {"name": str(obj["naming"]), "val_error": str(e)}
                )
                # print(f"{str(obj["naming"])}\n{e}\n\n")

    df_amo: DataFrame = df.loc[df["amo"].notna() & df["price"].notna()]
    amounts: list[dict] = df_amo.to_dict(orient="records")

    for amo_obj in amounts:
        try:
            amo_object = {
                "art": str(amo_obj["art"]),
                "price": amo_obj["price"],
                "amo": amo_obj["amo"],
            }
            amo_validated = Stock_ShinaTorg.model_validate(amo_object)
            validated_data["amo_data"].append(amo_validated.model_dump())
        except ValidationError as e:
            validated_data["no_amo_arts"].append(
                {"name": amo_object["art"], "val_error": str(e)}
            )
            print(f"{type(amo_object["price"])} - {amo_object["price"]}\n{e}\n\n")

    return validated_data
