from datetime import datetime
from typing import Any

from gspread import Worksheet
from gspread.utils import ValueRenderOption

from ..dicts import SeasonType
from ..sheets.fresh_stock import sort_stock
from ..sheets import STC, BASE_LAYOUT


async def fix_master_formulas(ws: Worksheet, table: str, supp: str):

    # Переделать чтобы все функции добавлялись вместе, а не по очерёдно
    def _construct_vlookup(supp: str, col: int, fr: str, to: str):
        """**Assemble VLOOKUP formula for Google Sheets.**

        :param supp: Supplier sheet name.
        :param col: [master table] Column number to update formula in.
        :param fr: [supplier table] **Start** of VLOOKUP range in supplier table.
        :param to: [supplier table] **End** of VLOOKUP range in supplier table.

        If our VLOOKUP range is just one column **fr** and **to** would be the same leter.\n
        But in case we collect data from several columns *fr* is a first column of the range and *to* is the last.
        """
        # art: str = BASE_LAYOUT["art"]["l"]
        art: str = STC[supp]["art"][
            "l"
        ]  # Supplier article column letter. VLOOKUP key for search range.
        ws.update_cell(
            2,
            col,
            (
                f"=LET(range,\n"
                f"  {{'{supp}'!${art}$3:${art},'{supp}'!${fr}$3:${to}}},\n"
                f'    ARRAYFORMULA( IFERROR( VLOOKUP(${art}$2:${art},range,SEQUENCE(1,COLUMNS(range)-1,2),FALSE),"")))'
            ),
        )

    #  -----------  ТЕХНИЧЕСКИЕ РАБОТЫ  -----------

    async def master_vlookup_update(
        main_from: str = "\nНаличие\n",  # Master table column from where we start
        main_to: str = "\nгод\n",  # Master table column where we end
    ):

        master_table_key_from: str = f"{supp}{main_from}"
        master_table_key_to: str = f"{supp}{main_to}"

        headers_array: list[str] = []
        formulas_array: list[str] = []

        master_column_names = list(STC[table].keys())
        try:
            start_idx = master_column_names.index(master_table_key_from)
            end_idx = master_column_names.index(master_table_key_to)
        except ValueError as e:
            raise KeyError(f"Ключ не найден в таблице {table}:\n{e}")

        headers_array = master_column_names[start_idx : end_idx + 1]
        print(headers_array)

        lookup_headers: dict[str, str] = {
            "\nНаличие\n": "Остаток\n",
            "\nΔ шт.\n": "Остаток\nΔ",
            "\nСтоимость\n": "Стоимость\n",
            "\nΔ цена\n": "Стоимость\nΔ",
            "\nгод\n": "year",
        }

        headers: list[str] = []
        today = datetime.today().strftime("%d.%m")

        for head in headers_array:

            headers.append(f"{head}{today}")

            key_head: str = head.replace(f"{supp}", "")
            supp_col: str = lookup_headers[key_head]

            ref = STC[supp][supp_col]["l"]
            art: str = STC[supp]["art"]["l"]
            vlookup_formula = (
                f"=LET(range,\n"
                f"  {{'{supp}'!${art}$3:${art},'{supp}'!${ref}$3:${ref}}},\n"
                f'    ARRAYFORMULA( IFERROR( VLOOKUP(${art}$2:${art},range,SEQUENCE(1,COLUMNS(range)-1,2),FALSE),"")))'
            )
            formulas_array.append(vlookup_formula)

        col_from = STC[table][master_table_key_from]["l"]
        col_to = STC[table][master_table_key_to]["l"]

        ws.update(
            values=[
                headers,
                formulas_array,
            ],
            range_name=f"{col_from}1:{col_to}2",
            value_input_option="USER_ENTERED",
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
            _construct_vlookup(supp=supp, col=col, fr=fr, to=to)

        col_fr = STC[table]["4tochki\nsolonkl\n"]["l"]
        col_to = STC[table]["4tochki\nΔ цена\n"]["l"]
        ws.update(
            values=[
                [
                    f"4tochki\nсол-цы\n{today}",
                    f"4tochki\nКРК2\n{today}",
                    f"4tochki\nΔ шт.\n{today}",
                    f"4tochki\nСтоимость\n{today}",
                    f"4tochki\nΔ цена\n{today}",
                ]
            ],
            range_name=f"{col_fr}1:{col_to}1",
            value_input_option="USER_ENTERED",
        )
    elif supp == list(STC)[3]:  # olta
        await master_vlookup_update()
        # cols = [
        #     {"col": f"{supp}\nНаличие\n", "ref": "Остаток\n"},
        #     {"col": f"{supp}\nΔ шт.\n", "ref": "Остаток\nΔ"},
        #     {"col": f"{supp}\nСтоимость\n", "ref": "Стоимость\n"},
        #     {"col": f"{supp}\nΔ цена\n", "ref": "Стоимость\nΔ"},
        #     {"col": f"{supp}\nсрок", "ref": "Срок"},
        # ]
        # for item in cols:
        #     col = STC[table][item["col"]]["n"]
        #     ref = STC[supp][item["ref"]]["l"]
        #     _construct_vlookup(supp=supp, col=col, fr=ref, to=ref)

        # col_fr = STC[table]["{supp}\nНаличие\n"]["l"]
        # col_to = STC[table]["{supp}\nсрок"]["l"]
        # ws.update(
        #     values=[
        #         [
        #             f"{supp}\nНаличие\n{today}",
        #             f"{supp}\nΔ шт.\n{today}",
        #             f"{supp}\nСтоимость\n{today}",
        #             f"{supp}\nΔ цена\n{today}",
        #             f"{supp}\nсрок\n{today}",
        #         ]
        #     ],
        #     range_name=f"{col_fr}1:{col_to}1",
        #     value_input_option="USER_ENTERED",
        # )
    elif supp == list(STC)[4]:  # shina_torg
        cols = [
            {"col": f"{supp}\nНаличие\n", "ref": "Остаток\n"},
            {"col": f"{supp}\nΔ шт.\n", "ref": "Остаток\nΔ"},
            {"col": f"{supp}\nСтоимость\n", "ref": "Стоимость\n"},
            {"col": f"{supp}\nΔ цена\n", "ref": "Стоимость\nΔ"},
            {"col": f"{supp}\nгод\n", "ref": "year"},
        ]
        for item in cols:
            col = STC[table][item["col"]]["n"]
            ref = STC[supp][item["ref"]]["l"]
            _construct_vlookup(supp=supp, col=col, fr=ref, to=ref)

        col_fr = STC[table][f"{supp}\nНаличие\n"]["l"]
        col_to = STC[table][f"{supp}\nгод\n"]["l"]
        ws.update(
            values=[
                [
                    f"{supp}\nНаличие\n{today}",
                    f"{supp}\nΔ шт.\n{today}",
                    f"{supp}\nСтоимость\n{today}",
                    f"{supp}\nΔ цена\n{today}",
                    f"{supp}\nгод\n{today}",
                ]
            ],
            range_name=f"{col_fr}1:{col_to}1",
            value_input_option="USER_ENTERED",
        )
    elif supp == list(STC)[5]:  # big_machine
        cols = [
            {"col": f"{supp}\nНаличие\n", "ref": "Остаток\n"},
            {"col": f"{supp}\nΔ шт.\n", "ref": "Остаток\nΔ"},
            {"col": f"{supp}\nСтоимость\n", "ref": "Стоимость\n"},
            {"col": f"{supp}\nΔ цена\n", "ref": "Стоимость\nΔ"},
        ]
        for item in cols:
            col = STC[table][item["col"]]["n"]
            ref = STC[supp][item["ref"]]["l"]
            _construct_vlookup(supp=supp, col=col, fr=ref, to=ref)

        col_fr = STC[table][f"{supp}\nНаличие\n"]["l"]
        col_to = STC[table][f"{supp}\nΔ цена\n"]["l"]
        ws.update(
            values=[
                [
                    f"{supp}\nНаличие\n{today}",
                    f"{supp}\nΔ шт.\n{today}",
                    f"{supp}\nСтоимость\n{today}",
                    f"{supp}\nΔ цена\n{today}",
                ]
            ],
            range_name=f"{col_fr}1:{col_to}1",
            value_input_option="USER_ENTERED",
        )
    elif supp == list(STC)[6]:  # simoshkevich
        cols = [
            {"col": f"{supp}\nНаличие\n", "ref": "Остаток\n"},
            {"col": f"{supp}\nΔ шт.\n", "ref": "Остаток\nΔ"},
            {"col": f"{supp}\nСтоимость\n", "ref": "Стоимость\n"},
            {"col": f"{supp}\nΔ цена\n", "ref": "Стоимость\nΔ"},
            {"col": f"{supp}\nгод\n", "ref": "year"},
        ]
        for item in cols:
            col = STC[table][item["col"]]["n"]
            ref = STC[supp][item["ref"]]["l"]
            _construct_vlookup(supp=supp, col=col, fr=ref, to=ref)

        col_from = STC[table][f"{supp}\nНаличие\n"]["l"]
        col_to = STC[table][f"{supp}\nгод\n"]["l"]
        ws.update(
            values=[
                [
                    f"{supp}\nНаличие\n{today}",
                    f"{supp}\nΔ шт.\n{today}",
                    f"{supp}\nСтоимость\n{today}",
                    f"{supp}\nΔ цена\n{today}",
                    f"{supp}\nгод\n{today}",
                ]
            ],
            range_name=f"{col_from}1:{col_to}1",
            value_input_option="USER_ENTERED",
        )


#  Переделать чтобы передавать только артикулы, без лишних данных
#  И убрать nan артикулы
async def common_tables_add_arts(
    n_data: list[dict[str, Any]], ws: Worksheet, table: str, supp: str
):

    new_arts: list[str] = []
    if n_data:
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

        if filtered_lines:

            sorted_stock: list[dict[str, Any]] = await sort_stock(filtered_lines)

            for line in sorted_stock:
                new_arts.append([line["art"]])

            ws.add_rows(len(new_arts) + 1)

            _l: str = BASE_LAYOUT["art"]["l"]
            number_last_row: int = len(ws.get("A3:A")) + 4

            ws.update(new_arts, f"{_l}{number_last_row}")

    return new_arts
