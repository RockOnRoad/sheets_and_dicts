from typing import Any, Generator

from gspread import Worksheet
from gspread.utils import ValueRenderOption

from ..sheets import STC


async def filter_new(
    data: list[dict[str, Any]], ws: Worksheet, table: str, supp: str
) -> Generator[dict[str, Any], None, None]:
    """**Filter out existing SKUs**\n
    Return a list of just new objects before using them further along.\n
    Prevents further code from running unnecessary validations and sorting.

    :param sheet: gspread.Worksheet - Where we collect existing articules. And upload new ones then.
    :param table: str - Table name - Which table we're gathering primary keys from.
    :param supp: str - Supplier name - So that we could use filtration by code with prefix for olta.
    :param data: A list of objects to filter.

    :return: A generator of objects that are not in the existing articules list.
    """

    if table == supp == list(STC)[3]:  # olta
        key: str = "Код с префиксом"
        letter: str = STC[supp]["code_w_prefix"]["l"]
    elif supp == list(STC)[2]:  # 4tochki
        key: str = "cae"
        letter: str = STC[supp]["art"]["l"]
    else:
        key: str = "art"
        letter: str = STC[supp][key]["l"]

    col = f"{letter}3:{letter}"

    ex_arts: list[str] = {
        item[0] if item else ""
        for item in ws.get(col, value_render_option=ValueRenderOption.unformatted)
    }

    #  Переносим условие от сюда в парсер
    fresh_stock: Generator[dict] = (obj for obj in data if obj[key] not in ex_arts)

    return fresh_stock
