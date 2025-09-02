import os
import gspread
from copy import deepcopy
from typing import Any

from gspread import Worksheet
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

#  If someone adds a new worksheet to the Google Sheet while app is running,
#  it won’t magically appear — because you cached the worksheets.
#  You’d have to re-import/reload the module or rebuild the worksheets dict if you need fresh ones.
#  If that’s a concern, just call _sh.worksheets() again when you need an update.

_gc = gspread.service_account(filename="app/sheets/credantials.json")
_sh = _gc.open_by_key(os.getenv("SHEET_ID"))
worksheets = {ws.title: ws for ws in _sh.worksheets()}


async def get_ws(name: str):
    """Fetch worksheet by name, quick lookup (no extra API call)."""
    return worksheets[name]


# async def sheets_conn(which_sheet: str = None) -> Worksheet | None:
#     scopes = [
#         "https://www.googleapis.com/auth/spreadsheets",
#     ]

#     creds = Credentials.from_service_account_file(
#         "app/sheets/credantials.json", scopes=scopes
#     )
#     client = gspread.authorize(creds)

#     sheet_id: str = os.getenv("SHEET_ID")

#     try:
#         sheet: Worksheet = client.open_by_key(sheet_id).worksheet(which_sheet)
#         return sheet
#     except gspread.exceptions.WorksheetNotFound:
#         return None

#  Main keys represent names of tables, secondary keys are names of columns

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

STC: dict[str, dict[str, dict[str, str | int]]] = {
    "Остатки поставщиков (зима)": {
        **deepcopy(BASE_LAYOUT),
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
        "4tochki\nsolonkl\n": {"l": "X", "n": 24},
        "4tochki\nkryarsk2\n": {"l": "Y", "n": 25},
        "4tochki\nΔ шт.\n": {"l": "Z", "n": 26},
        "4tochki\nСтоимость\n": {"l": "AA", "n": 27},
        "4tochki\nΔ цена\n": {"l": "AB", "n": 28},
        "olta\nСтоимость\nx4": {"l": "AC", "n": 29},
        "olta\nЦена\nx4": {"l": "AD", "n": 30},
        "olta\nНаличие\n": {"l": "AE", "n": 31},
        "olta\nΔ шт.\n": {"l": "AF", "n": 32},
        "olta\nСтоимость\n": {"l": "AG", "n": 33},
        "olta\nΔ цена\n": {"l": "AH", "n": 34},
        "olta\nсрок": {"l": "AI", "n": 35},
    },
    "Остатки поставщиков (лето)": {
        **deepcopy(BASE_LAYOUT),
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
        "4tochki\nsolonkl\n": {"l": "X", "n": 24},
        "4tochki\nkryarsk2\n": {"l": "Y", "n": 25},
        "4tochki\nΔ шт.\n": {"l": "Z", "n": 26},
        "4tochki\nСтоимость\n": {"l": "AA", "n": 27},
        "4tochki\nΔ цена\n": {"l": "AB", "n": 28},
        "olta\nСтоимость\nx4": {"l": "AC", "n": 29},
        "olta\nЦена\nx4": {"l": "AD", "n": 30},
        "olta\nНаличие\n": {"l": "AE", "n": 31},
        "olta\nΔ шт.\n": {"l": "AF", "n": 32},
        "olta\nСтоимость\n": {"l": "AG", "n": 33},
        "olta\nΔ цена\n": {"l": "AH", "n": 34},
        "olta\nсрок": {"l": "AI", "n": 35},
    },
    "4tochki": {
        **deepcopy(BASE_LAYOUT),
        "plus_2": {"l": "J", "n": 10},
        "plus_3": {"l": "K", "n": 11},
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
        "code_w_prefix": {"l": "J", "n": 10},
        "plus_2": {"l": "K", "n": 11},
        "plus_3": {"l": "L", "n": 12},
        "name": {"l": "M", "n": 13},
        "full_size": {"l": "N", "n": 14},
        "Срок": {"l": "O", "n": 15},
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
        "plus_3": {"l": "K", "n": 11},
        "plus_4": {"l": "L", "n": 12},
        "name": {"l": "M", "n": 13},
        "full_size": {"l": "N", "n": 14},
    },
    "big_shina": {
        **deepcopy(BASE_LAYOUT),
        "plus_2": {"l": "J", "n": 10},
        "plus_3": {"l": "K", "n": 11},
        "plus_4": {"l": "L", "n": 12},
        "name": {"l": "M", "n": 13},
        "full_size": {"l": "N", "n": 14},
    },
}
