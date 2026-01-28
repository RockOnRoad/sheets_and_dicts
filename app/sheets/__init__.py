import os
import gspread
from gspread.worksheet import Worksheet
from pathlib import Path

from copy import deepcopy

from dotenv import load_dotenv

load_dotenv()

#  If someone adds a new worksheet to the Google Sheet while app is running,
#  it won’t magically appear — because you cached the worksheets.
#  You’d have to re-import/reload the module or rebuild the worksheets dict if you need fresh ones.
#  If that’s a concern, just call _sh.worksheets() again when you need an update.

google_creds = Path(__file__).parent / "credantials.json"

_gc = gspread.service_account(filename=google_creds)
sh = _gc.open_by_key(os.getenv("SHEET_ID"))


def get_ws(name: str) -> Worksheet:
    """Fetch worksheet by name, quick lookup (no extra API call)."""
    return sh.worksheet(name)


BASE_LAYOUT: dict[str, dict[str, str | int]] = {
    "art": {"l": "A", "n": 1},
    "width": {"l": "B", "n": 2},
    "hei": {"l": "C", "n": 3},
    "diam": {"l": "D", "n": 4},
    "siz": {"l": "E", "n": 5},
    "lt": {"l": "F", "n": 6},  # l, t, m, z
    "seas": {"l": "G", "n": 7},
    "stud": {"l": "H", "n": 8},
    "supp": {"l": "I", "n": 9},
}

MASTER_LAYOUT: dict[str, dict[str, str | int]] = {
    "plus_2": {"l": "J", "n": 10},
    "plus_3": {"l": "K", "n": 11},
    "min_price": {"l": "L", "n": 12},
    "Ссылка\n(дром)": {"l": "M", "n": 13},
    "Модель": {"l": "N", "n": 14},
    "Маркировка": {"l": "O", "n": 15},
    "Цена\n(на дроме)": {"l": "P", "n": 16},
    "Сделал(а)": {"l": "Q", "n": 17},
    "Комментарий": {"l": "R", "n": 18},
    "Последнее\nобновление": {"l": "S", "n": 19},
    "Фактич.\nСтавка": {"l": "T", "n": 20},
    "Стандартная\nставка": {"l": "U", "n": 21},
    "4tochki\nСтоимость\nx4": {"l": "V", "n": 22},
    "4tochki\nЦена\nx4": {"l": "W", "n": 23},
    "4tochki\nсол-цы\n": {"l": "X", "n": 24},
    "4tochki\nКРК2\n": {"l": "Y", "n": 25},
    "4tochki\nΔ КРК2\n": {"l": "Z", "n": 26},
    "4tochki\nСтоимость\n": {"l": "AA", "n": 27},
    "4tochki\nΔ цена\n": {"l": "AB", "n": 28},
    "olta\nСтоимость\nx4": {"l": "AC", "n": 29},
    "olta\nЦена\nx4": {"l": "AD", "n": 30},
    "olta\nНаличие\n": {"l": "AE", "n": 31},
    "olta\nΔ шт.\n": {"l": "AF", "n": 32},
    "olta\nСтоимость\n": {"l": "AG", "n": 33},
    "olta\nΔ цена\n": {"l": "AH", "n": 34},
    "olta\nгод\n": {"l": "AI", "n": 35},
    "shina_torg\nСтоимость\nx4": {"l": "AJ", "n": 36},
    "shina_torg\nЦена\nx4": {"l": "AK", "n": 37},
    "shina_torg\nНаличие\n": {"l": "AL", "n": 38},
    "shina_torg\nΔ шт.\n": {"l": "AM", "n": 39},
    "shina_torg\nСтоимость\n": {"l": "AN", "n": 40},
    "shina_torg\nΔ цена\n": {"l": "AO", "n": 41},
    "shina_torg\nгод\n": {"l": "AP", "n": 42},
    "big_machine\nСтоимость\nx4": {"l": "AQ", "n": 43},
    "big_machine\nЦена\nx4": {"l": "AR", "n": 44},
    "big_machine\nНаличие\n": {"l": "AS", "n": 45},
    "big_machine\nΔ шт.\n": {"l": "AT", "n": 46},
    "big_machine\nСтоимость\n": {"l": "AU", "n": 47},
    "big_machine\nΔ цена\n": {"l": "AV", "n": 48},
    "simoshkevich\nСтоимость\nx4": {"l": "AW", "n": 49},
    "simoshkevich\nЦена\nx4": {"l": "AX", "n": 50},
    "simoshkevich\nНаличие\n": {"l": "AY", "n": 51},
    "simoshkevich\nΔ шт.\n": {"l": "AZ", "n": 52},
    "simoshkevich\nСтоимость\n": {"l": "BA", "n": 53},
    "simoshkevich\nΔ цена\n": {"l": "BB", "n": 54},
    "simoshkevich\nгод\n": {"l": "BC", "n": 55},
}

STC: dict[str, dict[str, dict[str, str | int]]] = {  # Supplier Table Configuration
    "Остатки поставщиков (зима)": {
        **deepcopy(BASE_LAYOUT),
        **deepcopy(MASTER_LAYOUT),
    },
    "Остатки поставщиков (лето)": {
        **deepcopy(BASE_LAYOUT),
        **deepcopy(MASTER_LAYOUT),
    },
    "4tochki": {
        **deepcopy(BASE_LAYOUT),
        "plus_2": {"l": "J", "n": 10},
        "supplier_naming": {"l": "K", "n": 11},
        "plus_4": {"l": "L", "n": 12},
        "name": {"l": "M", "n": 13},
        "full_size": {"l": "N", "n": 14},
        "Коммент": {"l": "O", "n": 15},
        "Стоимость\nΔ": {"l": "P", "n": 16},
        "solonkl\nΔ": {"l": "Q", "n": 17},
        "kryarsk2\nΔ": {"l": "R", "n": 18},
        "Стоимость\n": {"l": "S", "n": 19},
        "solonkl\n": {"l": "T", "n": 20},
        "kryarsk2\n": {"l": "U", "n": 21},
        "Стоимость": {"l": "V", "n": 22},
        "solonkl": {"l": "W", "n": 23},
        "kryarsk2": {"l": "X", "n": 24},
    },
    "olta": {
        **deepcopy(BASE_LAYOUT),
        "local_art": {"l": "J", "n": 10},
        "supplier_naming": {"l": "K", "n": 11},
        "plus_3": {"l": "L", "n": 12},
        "name": {"l": "M", "n": 13},
        "full_size": {"l": "N", "n": 14},
        "year": {"l": "O", "n": 15},
        "Коммент": {"l": "P", "n": 16},
        "Стоимость\nΔ": {"l": "Q", "n": 17},
        "Остаток\nΔ": {"l": "R", "n": 18},
        "Стоимость\n": {"l": "S", "n": 19},
        "Остаток\n": {"l": "T", "n": 20},
        "Стоимость": {"l": "U", "n": 21},
        "Остаток": {"l": "V", "n": 22},
    },
    "shina_torg": {
        **deepcopy(BASE_LAYOUT),
        "plus_2": {"l": "J", "n": 10},
        "supplier_naming": {"l": "K", "n": 11},
        "plus_4": {"l": "L", "n": 12},
        "name": {"l": "M", "n": 13},
        "full_size": {"l": "N", "n": 14},
        "year": {"l": "O", "n": 15},
        "Коммент": {"l": "P", "n": 16},
        "Стоимость\nΔ": {"l": "Q", "n": 17},
        "Остаток\nΔ": {"l": "R", "n": 18},
        "Стоимость\n": {"l": "S", "n": 19},
        "Остаток\n": {"l": "T", "n": 20},
        "Стоимость": {"l": "U", "n": 21},
        "Остаток": {"l": "V", "n": 22},
    },
    "big_machine": {
        **deepcopy(BASE_LAYOUT),
        "plus_2": {"l": "J", "n": 10},
        "supplier_naming": {"l": "K", "n": 11},
        "plus_4": {"l": "L", "n": 12},
        "name": {"l": "M", "n": 13},
        "full_size": {"l": "N", "n": 14},
        "year": {"l": "O", "n": 15},
        "Коммент": {"l": "P", "n": 16},
        "Стоимость\nΔ": {"l": "Q", "n": 17},
        "Остаток\nΔ": {"l": "R", "n": 18},
        "Стоимость\n": {"l": "S", "n": 19},
        "Остаток\n": {"l": "T", "n": 20},
        "Стоимость": {"l": "U", "n": 21},
        "Остаток": {"l": "V", "n": 22},
    },
    "simoshkevich": {
        **deepcopy(BASE_LAYOUT),
        "local_art": {"l": "J", "n": 10},
        "supplier_naming": {"l": "K", "n": 11},
        "plus_4": {"l": "L", "n": 12},
        "name": {"l": "M", "n": 13},
        "full_size": {"l": "N", "n": 14},
        "year": {"l": "O", "n": 15},
        "Коммент": {"l": "P", "n": 16},
        "Стоимость\nΔ": {"l": "Q", "n": 17},
        "Остаток\nΔ": {"l": "R", "n": 18},
        "Стоимость\n": {"l": "S", "n": 19},
        "Остаток\n": {"l": "T", "n": 20},
        "Стоимость": {"l": "U", "n": 21},
        "Остаток": {"l": "V", "n": 22},
    },
}
