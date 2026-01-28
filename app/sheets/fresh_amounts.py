from datetime import datetime
import random
from typing import Any

from aiogram.types import Message, CallbackQuery

from gspread import Worksheet
from app.services import MessageAnimation
from app.sheets.sheety_loops import make_safe_update, retryable

from . import STC


async def fix_formulas(upd: Message | CallbackQuery, ws: Worksheet, supp: str):
    safe_update = make_safe_update(ws)

    col = STC[supp]["Стоимость\nΔ"]["n"]  # Column with formula
    f_p = STC[supp]["Стоимость\n"]["l"]  # Fresh prices column
    p_p = STC[supp]["Стоимость"]["l"]  # Past prices column

    msg_animation = MessageAnimation(
        message_or_call=upd,
        base_text=f"<b>{supp}</b> запись - обновление формул",
    )
    await msg_animation.start()

    safe_update(
        2,
        col,
        f'=ARRAYFORMULA(IF(${f_p}$2:${f_p}>0,IF(${p_p}$2:${p_p}>0,${f_p}$2:${f_p}-${p_p}$2:${p_p},""),""))',
    )

    if supp == list(STC)[2]:  # 4tochki
        col = STC[supp]["solonkl\nΔ"]["n"]  # Column with formula
        f_s = STC[supp]["solonkl\n"]["l"]  # Fresh amounts at solonkl
        p_s = STC[supp]["solonkl"]["l"]  # Past amounts at solonkl
        safe_update(2, col, f"=ARRAYFORMULA(${f_s}$2:${f_s}-${p_s}$2:${p_s})")

        col = STC[supp]["kryarsk2\nΔ"]["n"]  # Column with formula
        f_s = STC[supp]["kryarsk2\n"]["l"]  # Fresh amounts at solonkl
        p_s = STC[supp]["kryarsk2"]["l"]  # Past amounts at solonkl
        safe_update(2, col, f"=ARRAYFORMULA(${f_s}$2:${f_s}-${p_s}$2:${p_s})")

    else:  # any other supplier
        col = STC[supp]["Остаток\nΔ"]["n"]  # Column with formula
        f_s = STC[supp]["Остаток\n"]["l"]
        p_s = STC[supp]["Остаток"]["l"]
        safe_update(2, col, f"=ARRAYFORMULA(${f_s}$2:${f_s}-${p_s}$2:${p_s})")

    await msg_animation.stop()


async def insert_amounts(upd: Message | CallbackQuery, data, ws: Worksheet, supp: str):
    """****

    :param data: `list[list[str, int | None]]` - grid of amounts and prices (correctly sorted)
    :param ws: `gspread.Worksheet` - Worksheet object to work with.
    :param supp: `str` - name of supplier. Used to reference all the right columns
    """
    today = datetime.today().strftime("%d.%m")

    # shared 2-column suppliers
    two_col = (list(STC)[3], list(STC)[4], list(STC)[5], list(STC)[6])

    if supp == list(STC)[2]:  # 4tochki
        headers = (
            [f"Стоимость\n{today}"],
            [f"solonkl\n{today}"],
            [f"kryarsk2\n{today}"],
        )
        start_key = "Стоимость\n"
        end_key = "kryarsk2\n"

    elif supp in two_col:
        headers = (
            [f"Стоимость\n{today}"],
            [f"Остаток\n{today}"],
        )
        start_key = "Стоимость\n"
        end_key = "Остаток\n"

    else:
        raise ValueError(f"Unknown supplier: {supp}")

    col = STC[supp][start_key]["n"]
    fr = STC[supp][start_key]["l"]
    to = STC[supp][end_key]["l"]

    # random color for the "I tried" effect
    r, g, b = (float(random.randint(0, x)) for x in (30, 15, 30))

    msg_animation_1 = MessageAnimation(
        message_or_call=upd,
        base_text=f"<b>{supp}</b> запись - исправление заголовков",
    )
    await msg_animation_1.start()

    retryable()(ws.insert_cols)(headers, col=col)

    await msg_animation_1.stop()

    msg_animation_2 = MessageAnimation(
        message_or_call=upd,
        base_text=f"<b>{supp}</b> запись - перекрашивание ячеек",
    )
    await msg_animation_2.start()

    retryable()(ws.format)(
        f"{fr}3:{to}", {"backgroundColor": {"red": r, "green": g, "blue": b}}
    )

    await msg_animation_2.stop()

    msg_animation_3 = MessageAnimation(
        message_or_call=upd,
        base_text=f"<b>{supp}</b> запись - количества и цены",
    )
    await msg_animation_3.start()

    retryable()(ws.update)(data, f"{fr}3")

    await msg_animation_3.stop()


async def prepare_amounts(
    keys: list[str], key: str, data: list[dict[str, Any]], supp: str
):

    amounts: list[list[str, int | None]] = []

    # supplier-specific field layouts
    layout = {
        list(STC)[2]: ("price", "amo_solonkl", "amo_kryarsk2"),  # 4tochki
        list(STC)[3]: ("price", "amo"),  # olta
        list(STC)[4]: ("price", "amo"),  # shina_torg
        list(STC)[5]: ("price", "amo"),  # big_machine
        list(STC)[6]: ("price", "amo"),  # simash
    }

    amo_columns = layout.get(supp)

    for pk in keys:
        if match := next((line for line in data if line[key] == pk), None):
            amounts.append(
                [match.get(f, 0 if f.startswith("amo") else None) for f in amo_columns]
            )
        else:
            # fallback: [None, 0, 0...] depending on number of amo_columns
            default = [None if f == "price" else 0 for f in amo_columns]
            amounts.append(default)

    return amounts


async def add_fresh_amounts(
    upd: Message | CallbackQuery, stock: list[dict[str, Any]], ws: Worksheet, supp: str
):
    """**Updates stock amounts.**\n
    Creates additional columns and populates them with new stock amounts.\n
    Compares SKUs by "art" or "code_w_prefix" and populates respective lines with appropriate amounts

    :param stock: `list[dict[str, Any]]` - List of stock objects.
    :param ws: `gspread.Worksheet` - Worksheet instance where the stock will be updated.
    :param supp: `str` - Name of supplier for correct dependancies
    """

    if supp in [list(STC)[3], list(STC)[6]]:  # olta; simoshkevich
        key: str = "local_art"
    else:
        key: str = "art"
    _l: str = STC[supp][key]["l"]
    col: str = f"{_l}3:{_l}"

    msg_animation_2 = MessageAnimation(
        message_or_call=upd,
        base_text=f"<b>{supp}</b> чтение - получение артикулов поставщика из таблицы",
    )
    await msg_animation_2.start()

    get_with_retry = retryable()(ws.get)
    primary_keys = get_with_retry(col)
    pks: list[str] = [item[0] if item else "" for item in primary_keys]
    # olta, simoshkevich - local_arts; others - arts

    await msg_animation_2.stop()

    grid_of_amos: list[str] = await prepare_amounts(
        keys=pks, key=key, data=stock, supp=supp
    )
    await insert_amounts(upd=upd, data=grid_of_amos, ws=ws, supp=supp)
    await fix_formulas(upd=upd, ws=ws, supp=supp)
