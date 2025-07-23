from gspread import Worksheet


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
