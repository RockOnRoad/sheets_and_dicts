from datetime import datetime
import random
from typing import Any

from gspread import Worksheet

from . import BASE_LAYOUT, STC


async def fix_formulas(ws: Worksheet, supp: str):
    col = STC[supp]["Стоимость\nΔ"]["n"]  # Column with formula
    f_p = STC[supp]["Стоимость\n"]["l"]  # Fresh prices column
    p_p = STC[supp]["Стоимость"]["l"]  # Past prices column
    ws.update_cell(
        2,
        col,
        f'=ARRAYFORMULA(IF(${f_p}$2:${f_p}>0,IF(${p_p}$2:${p_p}>0,${f_p}$2:${f_p}-${p_p}$2:${p_p},""),""))',
    )
    if supp == list(STC)[2]:  # 4tochki
        col = STC[supp]["solonkl\nΔ"]["n"]  # Column with formula
        f_s = STC[supp]["solonkl\n"]["l"]  # Fresh amounts at solonkl
        p_s = STC[supp]["solonkl"]["l"]  # Past amounts at solonkl
        ws.update_cell(2, col, f"=ARRAYFORMULA(${f_s}$2:${f_s}-${p_s}$2:${p_s})")

        col = STC[supp]["kryarsk2\nΔ"]["n"]  # Column with formula
        f_s = STC[supp]["kryarsk2\n"]["l"]  # Fresh amounts at solonkl
        p_s = STC[supp]["kryarsk2"]["l"]  # Past amounts at solonkl
        ws.update_cell(2, col, f"=ARRAYFORMULA(${f_s}$2:${f_s}-${p_s}$2:${p_s})")

    else:
        col = STC[supp]["Остаток\nΔ"]["n"]  # Column with formula
        f_s = STC[supp]["Остаток\n"]["l"]  # Fresh amounts at solonkl
        p_s = STC[supp]["Остаток"]["l"]  # Past amounts at solonkl
        ws.update_cell(2, col, f"=ARRAYFORMULA(${f_s}$2:${f_s}-${p_s}$2:${p_s})")
    # В виде формулы


async def insert_amounts(data, ws: Worksheet, supp: str):
    """****

    :param data:
    :param ws: 'gspread.Worksheet' - Worksheet object to work with.
    """

    r: int = float(random.randint(0, 30))
    g: int = float(random.randint(0, 15))
    b: int = float(random.randint(0, 30))

    today = datetime.today().strftime("%d.%m")

    if supp == list(STC)[2]:  # 4tochki
        headers: tuple = (
            [f"Стоимость\n{today}"],
            [f"solonkl\n{today}"],
            [f"kryarsk2\n{today}"],
        )
        col: int = STC[supp]["Стоимость\n"]["n"]
        fr: str = STC[supp]["Стоимость\n"]["l"]
        to: str = STC[supp]["kryarsk2\n"]["l"]
    elif supp == list(STC)[3]:  # olta
        headers: tuple = ([f"Стоимость\n{today}"], [f"Остаток\n{today}"])
        col: int = STC[supp]["Стоимость\n"]["n"]
        fr: str = STC[supp]["Стоимость\n"]["l"]
        to: str = STC[supp]["Остаток\n"]["l"]

    ws.insert_cols(headers, col=col)
    ws.format(f"{fr}3:{to}", {"backgroundColor": {"red": r, "green": g, "blue": b}})
    ws.update(data, f"{fr}3")


async def prepare_amounts(
    keys: list[str], key: str, data: list[dict[str, Any]], supp: str
):
    # wanted_keys: "art", "price", "amo_solonkl", "amo_kryarsk2"
    amounts: list[list[str, int | None]] = []

    if supp == list(STC)[2]:  # 4tochki
        for pk in keys:
            match = next((line for line in data if line[key] == pk), None)
            if match:
                amounts.append(
                    [
                        match.get("price"),
                        match.get("amo_solonkl", 0),
                        match.get("amo_kryarsk2", 0),
                    ]
                )
            else:
                amounts.append([None, 0, 0])
    elif supp == list(STC)[3]:  # olta
        for pk in keys:
            match = next((line for line in data if line[key] == pk), None)
            if match:
                amounts.append([match.get("price", None), match.get("amo", 0)])
            else:
                amounts.append([None, 0, 0])
    return amounts


async def add_fresh_amounts(stock: list[dict[str, Any]], ws: Worksheet, supp: str):

    if supp == list(STC)[3]:  # olta:
        key: str = "code_w_prefix"
    else:
        key: str = "art"
    letter: str = STC[supp][key]["l"]
    col: str = f"{letter}3:{letter}"

    pks: list[str] = [item[0] if item else "" for item in ws.get(col)]
    # 4tochki - arts; olta - code_w_prefix

    grid_of_amos: list[str] = await prepare_amounts(
        keys=pks, key=key, data=stock, supp=supp
    )
    await insert_amounts(data=grid_of_amos, ws=ws, supp=supp)
    await fix_formulas(ws=ws, supp=supp)
