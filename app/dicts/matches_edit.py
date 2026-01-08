import pathlib
import json

DICTS_DIR = pathlib.Path(__file__).parent


def json_to_dict(filename: str):
    # 1. Read JSON from file
    with open(f"{DICTS_DIR}/{filename}", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def back_to_json(data: dict, filename: str):
    # 3. Write it back
    with open(f"{DICTS_DIR}/{filename}", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


#  Добавляем новый бренд в model_matches.json
def add_brand_to_matches(brand: str):
    matches: dict = json_to_dict("model_matches.json")
    if brand not in matches.keys():
        matches[brand] = {}

    matches = dict(sorted(matches.items(), key=lambda item: item[0]))

    back_to_json(matches, "model_matches.json")


def add_name_to_matches(raw_name: str, proper_name: str, brand: str):
    matches: dict = json_to_dict("model_matches.json")
    if brand not in matches:
        matches[brand] = {}
    matches[brand][raw_name] = proper_name

    matches[brand] = dict(
        sorted(matches[brand].items(), key=lambda item: (-len(item[0]), item[1]))
    )

    back_to_json(matches, "model_matches.json")


def remove_name_from_matches(raw_name: str, brand: str):
    matches: dict = json_to_dict("model_matches.json")
    if brand in matches and raw_name in matches[brand]:
        del matches[brand][raw_name]

    back_to_json(matches, "model_matches.json")


#  json to dict -> edited dict to json


# # 2. Edit values (it's just a dict / list now)
# data["name"] = "Alex"
# data["counter"] += 1
# data["settings"]["enabled"] = False

# # 3. Write it back
# with open("data.json", "w", encoding="utf-8") as f:
#     json.dump(data, f, indent=4, ensure_ascii=False)
