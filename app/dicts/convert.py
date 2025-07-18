async def order_by(tires, parameter, key):
    ordered_by_key: dict = {}

    for value in parameter:
        ordered_by_key[value] = []
        for tire in tires:
            if tire.get(key, "").replace(" ", "_") == value:
                ordered_by_key[value].append(tires.pop(tires.index(tire)))

    # for item in ordered_by_key:
    #     print(item, ordered_by_key[item][:4])

    return ordered_by_key


async def remove_unnecessary_keys(tires):
    keys_to_remove = [
        "price_kryarsk2_rozn",
        "price_oh_krnekr",
        "price_oh_krnekr_rozn",
        "rest_oh_krnekr",
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
        "img_small",
        "img_big_pish",
        "protector_type",
        "market_model_id",
        "brand_info",
        "model_info",
        "num_layers_treadmil",
        "tread_width",
        "initial_tread_depth",
    ]
    for tire in tires:
        for key in keys_to_remove:
            tire.pop(key, None)
    return tires


async def seasons_list(tires) -> list:
    seasons = set(
        i.get("season", "") for i in tires if isinstance(i.get("season"), str)
    )
    return list(seasons)


async def brands_list(tires) -> list:
    brands = set(
        i.get("brand", "").replace(" ", "_")
        for i in tires
        if isinstance(i.get("brand"), str)
    )
    return list(brands)


async def arange_by_brand(json) -> dict:
    tires = json["tires"]

    brands: list = await brands_list(tires)
    # ["Yokohama", "Ikon Tyres", "Pirelli", ...]
    in_stock_tires: list = [tire for tire in tires if "price_kryarsk2" in tire]
    # [{'cae': 'F7640', 'gtin': 02900077764912, 'name': '...'}, {'cae': 'F7641', 'a': 3, 'b': 4}, ...]
    no_unnecessary_keys: list = await remove_unnecessary_keys(tires=in_stock_tires)
    # [{'cae': 'F7640', 'name': '***', ...}, {'cae': 'F7641', ...}, ...]
    stock_by_brand: dict = await order_by(
        tires=no_unnecessary_keys, parameter=brands, key="brand"
    )
    # {'Yokohama': [{'cae': 'R0229', 'name': ...}, {}, {}], 'Pirelli_Formula': [{'cae': '2177000', {}, {}], ...}

    return stock_by_brand


async def arange_by_season(json) -> dict:
    tires = json["tires"]

    seasons: list = await seasons_list(tires)  # ???
    in_stock_tires: list = [tire for tire in tires if "price_kryarsk2" in tire]
    # [{'cae': 'F7640', 'gtin': 02900077764912, 'name': '...'}, {'cae': 'F7641', 'a': 3, 'b': 4}, ...]
    no_unnecessary_keys: list = await remove_unnecessary_keys(tires=in_stock_tires)
    # [{'cae': 'F7640', 'name': '***', ...}, {'cae': 'F7641', ...}, ...]
    stock_by_season: dict = await order_by(
        tires=no_unnecessary_keys, parameter=seasons, key="season"
    )
    # ???

    return stock_by_season
