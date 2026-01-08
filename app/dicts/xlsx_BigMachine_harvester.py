from typing import Any

from gspread import Worksheet
from gspread.utils import ValueRenderOption
import pandas as pd
from pandas import ExcelFile, DataFrame
from pydantic import ValidationError, NonNegativeInt, model_validator

from app.dicts import TireSKU, TireStock, SeasonType, VehicleType
from app.sheets import STC
from app.sheets.parse_supplier_naming import parse_stud


class Stock_BigMashina(TireStock):
    art: str = ...
    amo: NonNegativeInt = 0

    @model_validator(mode="before")
    @classmethod
    def _build_line(cls, obj: dict[str, Any]):

        amo: int = 0
        try:
            amo = int(obj["amo"])
        except (ValueError, TypeError):
            amo = 20

        return {
            "art": str(obj.get("art", "")),
            "price": obj.get("price", None),
            "amo": amo,
        }


class SKU_BigMashina(TireSKU):
    # age: str | None = None

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
            "art": obj.get("art", None),
            "width": parsed_obj["width"],
            "hei": parsed_obj["height"],
            "diam": parsed_obj["diam"],
            "siz": siz,
            "lt": obj.get("lt", None),
            "seas": obj.get("seas", None),
            "stud": obj.get("stud", False),
            # "age": ...,
            "supp": "big_machine",
            "name": name,
            "full_size": full_size,
            "text": obj["naming"],
        }

        # # pattern = r"(?<!\d)(?:LT\s*)?(?:185|35)(?=[xX/ ]|$)"

        # def _extract_size(pattern, text) -> dict | dict[str, str]:
        #     if m := re.search(pattern, text):
        #         try:
        #             lt = m.group("lt")
        #         except AttributeError:
        #             lt = None

        #         try:
        #             width = m.group("width").replace(",", ".")
        #             width = float(width) if "." in width else int(width)
        #         except AttributeError:
        #             width = None

        #         try:
        #             hei = m.group("height").replace(",", ".")
        #             hei = float(hei) if "." in hei else int(hei)
        #         except AttributeError:
        #             hei = ""

        #         try:
        #             comercial = m.group("comercial")
        #         except AttributeError:
        #             comercial = None

        #         result = {
        #             "lt": lt,
        #             "width": width,
        #             "height": hei,
        #             "comercial": comercial,
        #         }
        #     else:
        #         result = {
        #             "lt": None,
        #             "width": None,
        #             "height": None,
        #             "comercial": None,
        #         }
        #     return result

        # size_pattern = (
        #     r"(?:"
        #     r"(?:(?P<lt>LT)?)"
        #     r"(?:(?P<width>\d{2,3})[/xX*]?)?"
        #     r"(?:(?P<height>\d{1,2}(?:[,.]\d{1,2})?))?"
        #     r"(?:(?P<comercial> C))?"
        #     r")"
        # )
        # size_extract: dict[str, str] = _extract_size(size_pattern, obj["width_and_hei"])

        # siz: str = (
        #     f"{size_extract.get("width")}{size_extract.get("height")}{obj.get("diam", "")}{obj.get("comercial", "")}"
        # )

        # def _extract(find: str, text: str = obj.get("naming", "")) -> str:
        #     found = False
        #     if find in text:
        #         found = True
        #     return found

        # def _extract_value(names_ali: dict, text: str = obj.get("naming", "")) -> str:
        #     text_upper = text.upper().replace("_", " ")
        #     for name_raw, name_std in names_ali.items():
        #         if _extract(text=text_upper, find=name_raw):
        #             return name_std
        #     return "?"

        # try:
        #     brand: str = _extract_value(
        #         names_ali=names.BRANDS, text=obj.get("brand", "")
        #     )
        # except KeyError:
        #     brand = "?"

        # try:
        #     model: str = _extract_value(names_ali=names.MODELS[brand])
        # except KeyError:
        #     model = "?"

        # suv: str = " SUV" if _extract(find=" SUV ") else ""
        # xl: str = " XL" if _extract(find=" XL") else ""

        # indexes_pattern = r"(?P<indexes>\d{2,3}(?:/\d{2,3})?(?:[A-ZТ]|ZR))"
        # indexes = (
        #     m.group()
        #     if (m := re.search(indexes_pattern, obj.get("naming", "")))
        #     else ""
        # )

        # _d = f"R{obj["diam"]}" if obj["diam"] else ""
        # full_size = (
        #     f"{size_extract.get("width")}/{size_extract.get("height")}{_d}{obj.get("comercial", "")} "
        #     f"{indexes}{xl}"
        # )

        # return {
        #     "art": obj.get("art", None),
        #     "width": (
        #         size_extract.get("width") if isinstance(size_extract, dict) else None
        #     ),
        #     "hei": (
        #         size_extract.get("height") if isinstance(size_extract, dict) else ""
        #     ),
        #     "diam": obj.get("diam", None),
        #     "siz": siz,
        #     "lt": obj.get("lt", None),
        #     "seas": obj.get("seas", None),
        #     "stud": obj.get("stud", False),
        #     # "age": ...,
        #     "supp": "big_machine",
        #     "name": f"{brand} {model}{suv}",
        #     "full_size": full_size,
        #     "text": "",
        # }


async def harv_big_machine(xlsx: ExcelFile, ws: Worksheet) -> None:
    """**Parser for Excel from big_mashina**\n

    Structures information from Excel document.

    :param xlsx: `pd.ExcelFile` List of SKUs, where each object is 1 row of Excel document.
    :param ws: Connected google sheets table `big_mashina`. We can use `ws.get()`, `ws.update()` with it.
    :return: `dict[str, list]`\n
    `"new_lines"` - A list of **TireSKU** objects, with articles that aren't present in a table.\n
    `"amo_data"` - A list of all **TireStock** objects.\n
    `"trash_lines"` - A list of object names, which haven't passed **TireSKU** validation.
    And their ValidationErrors\n
    `"no_amo_arts"` - A list of articles of SKUs, which havent passed **TireStock** validation.
    And their ValidationErrors\n
    """

    tables: list[dict] = [
        {
            "sheet_name": "Зимние",
            "lt": VehicleType.LIGHT,
            "seas": SeasonType.WINTER,
            "art": "Unnamed: 0",
            "price": "Unnamed: 5",
            "amo": "Unnamed: 11",
        },
        {
            "sheet_name": "Летние",
            "lt": VehicleType.LIGHT,
            "seas": SeasonType.SUMMER,
            "art": "Unnamed: 0",
            "price": "Unnamed: 5",
            "amo": "Unnamed: 11",
        },
        {
            "sheet_name": "Легкогрузовые",
            "lt": VehicleType.LIGHTTRUCK,
            "seas": SeasonType.WINTER,
            "art": "Unnamed: 0",
            "price": "Unnamed: 5",
            "amo": "Unnamed: 12",
        },
    ]

    validated_data = {
        "i_data": 0,  # int
        "new_lines": [],  # list[dict[str, Any]]
        "amo_data": [],  # list[dict[str, int | None]]
        "trash_lines": [],  # list[dict[str, Any]]
        "no_amo_arts": [],  # list[dict[str, Any]]
    }

    _l: str = STC["shina_torg"]["art"]["l"]
    ex_arts: set[str] = {
        item[0] if item else ""
        for item in ws.get(
            f"{_l}3:{_l}", value_render_option=ValueRenderOption.unformatted
        )
    }

    for table in tables:
        df: DataFrame = pd.read_excel(xlsx, table["sheet_name"])
        df: DataFrame = df[df[table["amo"]].notna()]

        df_filtered: DataFrame = df[~df[table["art"]].isin(ex_arts)]
        df_filtered: DataFrame = df[
            df[table["art"]].notna() & ~df[table["art"]].isin(ex_arts)
        ]
        df_amounts: DataFrame = df[[table["art"], table["price"], table["amo"]]]

        new_SKUs: list[dict[str, Any]] = df_filtered.to_dict(orient="records")

        for sku in new_SKUs:
            if sku[table["art"]] == "Артикул производителя":
                continue

            validated_data["i_data"] += 1

            try:
                sku_object = {
                    "art": str(sku[table["art"]]),
                    "naming": str(sku["Unnamed: 1"]).upper(),
                    "diam": str(sku["Unnamed: 2"]),
                    "width_and_hei": str(sku["Unnamed: 3"]),
                    "brand": str(sku["Unnamed: 4"]),
                    "lt": table["lt"],
                    "seas": table["seas"],
                    "stud": (
                        True
                        if str(sku[list(sku.keys())[-1]]).lower() == "шипованные"
                        else False
                    ),
                }
                sku_validated = SKU_BigMashina.model_validate(sku_object)
                validated_data["new_lines"].append(sku_validated.model_dump())
            except ValidationError as e:
                validated_data["trash_lines"].append(
                    {"name": str(sku["Unnamed: 1"]), "val_error": str(e)}
                )

        fresh_amounts: list[dict[str, Any]] = df_amounts.to_dict(orient="records")

        for amo_obj in fresh_amounts:
            if amo_obj[table["art"]] == "Артикул производителя":
                continue
            try:
                amo_object = {
                    "art": str(amo_obj[table["art"]]),
                    "amo": amo_obj[table["amo"]],
                    "price": amo_obj[table["price"]].replace(" ", "").strip(),
                }
                amo_validated = Stock_BigMashina.model_validate(amo_object)
                validated_data["amo_data"].append(amo_validated.model_dump())
            except ValidationError as e:
                validated_data["no_amo_arts"].append(
                    {"name": amo_object["art"], "val_error": str(e)}
                )

    return validated_data
