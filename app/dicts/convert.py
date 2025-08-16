import re
from re import Match
from app.sheets import sheets_conn

from ..sheets.add_rows import sort_stock


async def remove_unnecessary_keys(tires):
    """Облегчает полученный из json файла словарь, удаляя из него не нужные ключи."""

    keys_to_remove = (
        "price_kryarsk2_rozn",
        "price_oh_krnekr",
        "price_oh_krnekr_rozn",
        "rest_oh_krnekr",
        "price_oh_bilkal",
        "price_oh_bilkal_rozn",
        "rest_oh_bilkal",
        "price_ok_katsev",
        "price_ok_katsev_rozn",
        "rest_ok_katsev",
        "price_yamka",
        "price_yamka_rozn",
        "rest_yamka",
        "price_dvdv",
        "price_dvdv_rozn",
        "rest_dvdv",
        "gtin",
        "diametr_out",
        "thorn_type",
        "tech",
        "protection",
        "usa",
        "omolog",
        "side",
        "axle",
        "sloy",
        "grip",
        "img_small",
        "img_big_pish",
        "protector_type",
        "market_model_id",
        "brand_info",
        "model_info",
        "num_layers_treadmil",
        "tread_width",
        "initial_tread_depth",
    )
    for line in tires:
        for key in keys_to_remove:
            # line.pop(key, None)
            if key in line:
                del line[key]
    return tires


async def divide_by_key(data: list, param: str) -> dict:
    """Проходит по списку словарей, находит уникальные значения ключа {param}\n
    и составляет словарь с ключами из этих уникальных значений.\n
    После добавляет каждый словарь из начального списка в список, ключом которого является значение его параметра.
    """

    stock_by_param: dict = {}
    for i in data:
        key = i.get(param, "-")
        stock_by_param.setdefault(key, []).append(i)
    return stock_by_param


async def fix_casing(s):
    """Capitalize only the first segment before underscore."""
    return " ".join(part.capitalize() for part in s.split("_"))


async def olta_xls_pretty(data: list[dict], pd) -> list[dict]:

    parsed_lines: list[dict] = []

    season: int = 0  # 0-none, 1-ЗИМНИЕ, 2-ЛЕТНИЕ
    car_type: int = 0  # 0-none, 1-ЛЕГКОВЫЕ, 2-ЛЕГКОГРУЗОВЫЕ
    for line in data:
        if pd.notna(line["Номенклатура"]):
            if "ЗИМНИЕ" in line["Номенклатура"]:
                season = 1
                continue
            elif "ЛЕТНИЕ" in line["Номенклатура"]:
                season = 2
                continue

            if "ЛЕГКОВЫЕ" in line["Номенклатура"]:
                car_type = 1
                continue
            elif "ЛЕГКОГРУЗОВЫЕ" in line["Номенклатура"]:
                car_type = 2
                continue
            elif "ГРУЗОВЫЕ" in line["Номенклатура"]:
                break

        
        if pd.notna(line["Красноярск"]):
            amount: int = line["Красноярск"] if isinstance(line["Красноярск"], int) else 20
        else:
            amount: int = 0

        
        if amount > 0 and pd.notna(line["Код с префиксом"]):

            async def fix_type(value, target_type):
                if pd.notna(value):
                    try:
                        return target_type(value)
                    except (ValueError, TypeError):
                        return target_type()  # 0 for int, '' for str
                else:
                    return target_type()
                

            pattern = re.compile(
                r"\s+"
                r"(?:"
                r"(?:(?P<width>\d{1,3})[x/]?)?"
                r"(?:(?P<height>\d{1,2}(?:[,.]\d{1,2})?))?"
                r"\s+(?P<diameter>Z?R\d{2}(?:[,.]\d)?[CС]?)"
                r")\s+"
                r"(?P<brand>[^\s]+)\s+"
                r"(?P<model>.+?)\s+"
                r"(?P<indexes>\d{2,3}(?:/\d{2,3})?(?:[A-ZТ]|ZR))"
                r"(?:\s+(?P<xl>XL)(?=\s|$))?"
                r"(?:\s+(?P<spikes>Ш)(?=\s|$))?"
                r"(?:\s+(?P<suv>SUV)(?=\s|$))?"
            )

            m = pattern.search(line["Номенклатура"])
            params = {}
            if m:
                params = m.groupdict()
            full_code = await fix_type(line.get("Код с префиксом", ""), str)
            art = await fix_type(line.get("Артикул ", ""), str)
            name = await fix_type(line.get("Номенклатура", ""), str)

            width = await fix_type(params.get("width", 0), int)
            height = await fix_type(params.get("height", 0), int)
            diameter = await fix_type(params.get("diameter", ""), str)
            if height:
                size = f"{str(width)}/{str(height)} {str(diameter)}"
            else:
                size = f"{str(width)} {str(diameter)}"

            brand_fix = await fix_type(params.get("brand", ""), str)
            brand = await fix_casing(brand_fix)
            model_fix = await fix_type(params.get("model", ""), str)
            model = await fix_casing(model_fix)
            age = await fix_type(line.get("Харктеристика номенклатуры", ""), str)

            suv = params.get("suv", "")

            marking = brand + " " + model

            ind = params.get("indexes", "")
            xl = params.get("xl", "")
            spikes = params.get("spikes", "")

            full_size = size + (f" {ind}" if ind else "") + (f" {xl}" if xl else "")
            
            car_type_map: dict = {1: "light", 2: "lt"}
            season_map: dict = {1: "winter", 2: "summer"}

            price = await fix_type(line.get("Цена с основного склада за п/о", 0), int)


            d = {
                "full_code": full_code,
                "art": art,
                "name": name,
                "brand": brand,
                "model": model,
                "suv": suv,
                "marking": marking, 
                "width": width,
                "height": height,
                "diameter": diameter,
                "size": size,
                "siz": f"{width}{height}{re.sub(r"^R(\d{2}(?:[,.]\d)?)(?:[CС])?$", r"\1", diameter)}",
                "indexes": ind,
                "xl": xl,
                "spikes": spikes,
                "full_size": full_size,
                "age": age,
                "lt": car_type_map.get(car_type, ""),
                "season": season_map.get(season, ""),
                "amount": amount,
                "price": price,
            }
            parsed_lines.append(d)

    sorted_lines: list[dict] = sorted(parsed_lines, key=lambda x: (x["brand"], x["model"], x["diameter"], x["width"], x["height"], x["full_code"]))

    # for line in sorted_lines[892:942]:
    #     print(line)

    return sorted_lines


async def olta_xls_sort(data) -> dict:
    pass
