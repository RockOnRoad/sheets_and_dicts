import re
from typing import Any

from gspread import Worksheet
from gspread.utils import ValueRenderOption
import pandas as pd
from pydantic import ValidationError, NonNegativeInt, model_validator

from app.dicts import names
from app.dicts import TireSKU, TireStock, SeasonType, VehicleType
from app.sheets import STC


class Stock_ShinaTorg(TireStock):
    art: str = ...
    amo: NonNegativeInt = 0

    @model_validator(mode="before")
    @classmethod
    def _build_line(cls, line: dict[str, Any]):

        amo = (
            line.get("Основной склад", 0)
            if isinstance(line["Основной склад"], int)
            else 50
        )
        return {
            "art": str(line.get("Артикул", "")),
            "price": line.get("крупный опт", None),
            "amo": amo,
        }


class SKU_ShinaTorg(TireSKU):
    age: str | None = None

    @model_validator(mode="before")
    @classmethod
    def _build_line(cls, obj: dict[str, Any]):

        def _extract_size(pattern, text) -> dict | dict[str, str]:
            if m := re.search(pattern, text):
                full_match = m.group()
                try:
                    width = m.group("width").replace(",", ".")
                    width = float(width) if "." in width else int(width)
                except AttributeError:
                    width = None

                try:
                    hei = m.group("height").replace(",", ".")
                    hei = float(hei) if "." in hei else int(hei)
                except AttributeError:
                    hei = ""

                diam = m.group("diameter")
                diam = re.sub(r"[^0-9.,]", "", diam)
                diam = diam.replace(",", ".")

                result = {
                    "full": full_match,
                    "width": width,
                    "height": hei,
                    "diameter": diam,
                    "rest": text.replace(full_match, "", 1).strip(),
                }
            else:
                result = {
                    "full": None,
                    "width": None,
                    "height": None,
                    "diameter": None,
                    "rest": text.strip(),
                }
            return result

        size_pattern = (
            r"(?:"
            r"(?:(?P<width>\d{2,3})[/xX*]?)?"
            r"(?:(?P<height>\d{1,2}(?:[,.]\d{1,2})?))?"
            r"\s*(?P<diameter>(?:(?:RZ|Z)?R)\d{2}(?:[,.]\d)?(?:[CС]|LT)?)"
            r") "
        )
        size_extract: dict[str, str] = _extract_size(size_pattern, obj["naming"])
        rest_text: str = size_extract["rest"].replace("_", " ")
        # print(size_extract.get("full"))
        # print(size_extract.get("width"))
        # print(size_extract.get("height"))
        # print(size_extract.get("diameter"))
        # print(size_extract.get("rest"))

        siz: str = (
            f"{size_extract.get("width")}{size_extract.get("height")}{size_extract.get("diameter")}"
        )

        indexes_pattern = r"(?P<indexes>\d{2,3}(?:/\d{2,3})?\s?(?:[A-ZТ]|ZR))"
        indexes = m.group() if (m := re.search(indexes_pattern, rest_text)) else ""

        year_pattern = r"(?:(?P<year>\d{4}) ГОД)"
        year = m.group("year") if (m := re.search(year_pattern, rest_text)) else ""

        def _extract(find: str, text: str = rest_text) -> str:
            found = False
            if find in text:
                found = True
            return found

        def _extract_value(names_ali: dict, text: str = rest_text) -> str:
            text_upper = text.upper().replace("_", " ")
            for name_raw, name_std in names_ali.items():
                if _extract(text=text_upper, find=name_raw):
                    return name_std
            return "?"  # or a fallback

        try:
            brand: str = _extract_value(names_ali=names.BRANDS)
        except KeyError:
            brand = "?"

        try:
            model: str = _extract_value(names_ali=names.MODELS[brand])
        except KeyError:
            model = "?"

        for n in names.SPOKES:
            stud = _extract(find=n)
            if stud:
                break

        suv: str = " SUV" if _extract(find=" SUV ") else ""
        xl: str = " XL" if _extract(find=" XL") else ""

        return {
            "art": obj.get("art", None),
            "width": (
                size_extract.get("width") if isinstance(size_extract, dict) else None
            ),
            "hei": (
                size_extract.get("height") if isinstance(size_extract, dict) else ""
            ),
            "diam": (
                size_extract.get("diameter") if isinstance(size_extract, dict) else None
            ),
            "siz": siz,
            "lt": obj.get("lt", None),
            "seas": obj.get("seas", None),
            "stud": stud,
            "age": year,
            "supp": "shina_torg",
            "name": f"{brand} {model}{suv}",  # + SUV
            "full_size": f"{size_extract["full"]}{indexes}{xl}",
        }


async def harv_shina_torg(raw_data: list[dict[str, Any]], ws: Worksheet) -> None:
    """**Parser for Excel from shina-torg**\n

    Structures information from Excel document.

    :param raw_data: `list[dict[str, Any]]` List of SKUs, where each object is 1 row of Excel document.
    :param ws: Connected google sheets table `shina_torg`. We can use `ws.get()`, `ws.update()` with it.
    :return: `dict[str, list]`\n
    `"new_lines"` - A list of **TireSKU** objects, with articles that aren't present in a table.\n
    `"amo_data"` - A list of all **TireStock** objects.\n
    `"trash_lines"` - A list of object names, which haven't passed **TireSKU** validation.
    And their ValidationErrors\n
    `"no_amo_arts"` - A list of articles of SKUs, which havent passed **TireStock** validation.
    And their ValidationErrors\n
    """

    validated_data = {
        "i_data": len(raw_data),
        "new_lines": [],  # list[dict[str, Any]]
        "trash_lines": [],  # list[dict[str, Any]]
        "amo_data": [],  # list[dict[str, int | None]]
        "no_amo_arts": [],  # list[dict[str, Any]]
    }

    l: str = STC["shina_torg"]["art"]["l"]

    ex_arts: list[str] = {
        item[0] if item else ""
        for item in ws.get(
            f"{l}3:{l}", value_render_option=ValueRenderOption.unformatted
        )
    }

    seas: str = None  # None, w, s
    lt: str = None  # None, l, lt

    # row = 0
    for obj in raw_data:  # ????
        # row += 1
        if pd.notna(obj["Номенклатура"]):

            if "зима" in obj["Номенклатура"].lower():
                seas = SeasonType.WINTER
            elif "лето" in obj["Номенклатура"].lower():
                seas = SeasonType.SUMMER
            elif "всесезонные" in obj["Номенклатура"].lower():
                seas = SeasonType.ALLSEASON

            if "легковые" in obj["Номенклатура"].lower():
                lt = VehicleType.LIGHT
                continue
            elif "легкогрузовые" in obj["Номенклатура"].lower():
                lt = VehicleType.LIGHTTRUCK
                continue
            elif "грузовые" in obj["Номенклатура"].lower():
                break

        if pd.notna(obj["Основной склад"]) and pd.notna(obj["Артикул"]):
            if obj["Артикул"] not in ex_arts:
                new_obj = {
                    "art": str(obj["Артикул"]),
                    "naming": str(obj["Номенклатура"]).upper(),
                    "lt": lt,
                    "seas": seas,
                    "amo": obj["Основной склад"],
                    "price": obj["крупный опт"],
                }
                try:
                    sku = SKU_ShinaTorg.model_validate(new_obj)
                    validated_data["new_lines"].append(sku.model_dump())
                except ValidationError as e:
                    # print(f"{row}*** {new_obj["naming"]}\n{e}")
                    validated_data["trash_lines"].append(
                        {"name": new_obj["naming"], "val_error": str(e)}
                    )
            try:
                amo = Stock_ShinaTorg.model_validate(obj)
                validated_data["amo_data"].append(amo.model_dump())
            except ValidationError as e:
                validated_data["no_amo_arts"].append(
                    {"name": obj["Артикул"], "val_error": str(e)}
                )

    return validated_data
