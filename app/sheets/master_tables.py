from datetime import datetime
from typing import Any

from gspread import Worksheet
from gspread.utils import ValueRenderOption

from ..dicts import SeasonType
from ..sheets.fresh_stock import sort_stock
from ..sheets import STC, BASE_LAYOUT


async def fix_master_formulas(ws: Worksheet, table: str, supp: str):

    def construct_vlookup(supp: str, col: int, fr: str, to: str):
        art: str = BASE_LAYOUT["art"]["l"]
        ws.update_cell(
            2,
            col,
            (
                f"=LET(range,\n"
                f"  {{'{supp}'!${art}$3:${art},'{supp}'!${fr}$3:${to}}},\n"
                f'    ARRAYFORMULA( IFERROR( VLOOKUP(${art}$2:${art},range,SEQUENCE(1,COLUMNS(range)-1,2),FALSE),"")))'
            ),
        )

    today = datetime.today().strftime("%d.%m")
    if supp == list(STC)[2]:  # 4tochki
        cols = [
            {"col": "4tochki\nsolonkl\n", "fr": "solonkl\n", "to": "kryarsk2\n"},
            {"col": "4tochki\nΔ шт.\n", "fr": "kryarsk2\nΔ", "to": "kryarsk2\nΔ"},
            {
                "col": "4tochki\nСтоимость\n",
                "fr": "Стоимость\n",
                "to": "Стоимость\n",
            },
            {
                "col": "4tochki\nΔ цена\n",
                "fr": "Стоимость\nΔ",
                "to": "Стоимость\nΔ",
            },
        ]
        for item in cols:
            col = STC[table][item["col"]]["n"]
            fr = STC[supp][item["fr"]]["l"]
            to = STC[supp][item["to"]]["l"]
            construct_vlookup(supp=supp, col=col, fr=fr, to=to)

        col_fr = STC[table]["4tochki\nsolonkl\n"]["l"]
        col_to = STC[table]["4tochki\nΔ цена\n"]["l"]
        ws.update(
            values=[
                [
                    f"4tochki\nsolonkl\n{today}",
                    f"4tochki\nkryarsk2\n{today}",
                    f"4tochki\nΔ шт.\n{today}",
                    f"4tochki\nСтоимость\n{today}",
                    f"4tochki\nΔ цена\n{today}",
                ]
            ],
            range_name=f"{col_fr}1:{col_to}1",
            value_input_option="USER_ENTERED",
        )
    elif supp == list(STC)[3]:  # olta
        cols = [
            {"col": "olta\nНаличие\n", "ref": "Остаток\n"},
            {"col": "olta\nΔ шт.\n", "ref": "Остаток\nΔ"},
            {"col": "olta\nСтоимость\n", "ref": "Стоимость\n"},
            {"col": "olta\nΔ цена\n", "ref": "Стоимость\nΔ"},
            {"col": "olta\nсрок", "ref": "Срок"},
        ]
        for item in cols:
            col = STC[table][item["col"]]["n"]
            ref = STC[supp][item["ref"]]["l"]
            construct_vlookup(supp=supp, col=col, fr=ref, to=ref)

        col_fr = STC[table]["olta\nНаличие\n"]["l"]
        col_to = STC[table]["olta\nсрок"]["l"]
        ws.update(
            values=[
                [
                    f"olta\nНаличие\n{today}",
                    f"olta\nΔ шт.\n{today}",
                    f"olta\nСтоимость\n{today}",
                    f"olta\nΔ цена\n{today}",
                    f"olta\nсрок\n{today}",
                ]
            ],
            range_name=f"{col_fr}1:{col_to}1",
            value_input_option="USER_ENTERED",
        )


async def common_tables_add_arts(
    n_data: list[list[str]], ws: Worksheet, table: str, supp: str
):

    ex_arts: set[str] = {
        item[0]
        for item in ws.get(
            range_name="A3:A", value_render_option=ValueRenderOption.unformatted
        )
        if item
    }
    new_lines: set[str] = (obj for obj in n_data if obj["art"] not in ex_arts)

    filtered_lines: list[dict[str, Any]] = []
    if table == list(STC)[0]:
        seas = (SeasonType.WINTER, SeasonType.ALLSEASON)
    elif table == list(STC)[1]:
        seas = (SeasonType.SUMMER,)
    for line in new_lines:
        if line["lt"] == "l" and line["seas"] in seas:
            filtered_lines.append(line)

    new_arts: list[str] = []
    if filtered_lines:

        sorted_stock: list[dict[str, Any]] = await sort_stock(filtered_lines)

        for line in sorted_stock:
            new_arts.append([line["art"]])

        ws.add_rows(len(new_arts) + 1)

        l: str = BASE_LAYOUT["art"]["l"]
        number_last_row: int = len(ws.get("A3:A")) + 4

        ws.update(new_arts, f"{l}{number_last_row}")

    await fix_master_formulas(ws=ws, table=table, supp=supp)

    return new_arts
