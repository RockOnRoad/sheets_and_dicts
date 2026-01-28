import asyncio

from datetime import datetime
from typing import Any

from aiogram.types import Message, CallbackQuery
from gspread import Worksheet
from gspread.utils import ValueRenderOption
from pandas import notna

from ..dicts import SeasonType
from ..sheets.fresh_stock import sort_stock
from ..sheets import STC, BASE_LAYOUT
from app.services import MessageAnimation
from app.sheets.sheety_loops import retryable


async def fix_master_formulas(
    upd: Message | CallbackQuery, ws: Worksheet, table: str, supp: str
):
    """**Updates Headers and repairs Formulas that load amounts from suppliers tables to master tables**

    :param ws: `gspread.Worksheet` Sheet, we work with
    :param table: `str` Name of the sheet we work with
    :param supp: `str` Name of a supplier we update
    """

    async def master_vlookup_update(
        main_from: str = "\nНаличие\n",  # Master table column from where we start
        main_to: str = "\nгод\n",  # Master table column where we end
    ):
        """**Shapes 2 first suppliers rows in a master table. Headers and Formulas**

        Iterates through supplier specific columns of a master table
        and assambles a header and a vlookup formula in each column.

        Goes through each column from **main_from** to **main_to**
        assembling an up-to-date header for row 1 and fixing a formula in row 2

        :param main_from: `str` Master table column from where supplier data start
        :param main_to: `str` Master table column where supplier data end
        """

        lookup_headers: dict[str, str] = {
            "\nсол-цы\n": "solonkl\n",
            "\nКРК2\n": "kryarsk2\n",
            "\nΔ КРК2\n": "kryarsk2\nΔ",
            "\nНаличие\n": "Остаток\n",
            "\nΔ шт.\n": "Остаток\nΔ",
            "\nСтоимость\n": "Стоимость\n",
            "\nΔ цена\n": "Стоимость\nΔ",
            "\nгод\n": "year",
        }

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

        msg_animation = MessageAnimation(
            message_or_call=upd,
            base_text=f"<b>{table}</b> запись - обновление формул и заголовков",
        )
        await msg_animation.start()

        retryable()(ws.update)(
            values=[
                headers,
                formulas_array,
            ],
            range_name=f"{col_from}1:{col_to}2",
            value_input_option="USER_ENTERED",
        )

        await msg_animation.stop()

    if supp in list(STC)[2:]:
        if supp == list(STC)[2]:  # 4tochki
            await master_vlookup_update(main_from="\nсол-цы\n", main_to="\nΔ цена\n")
        elif supp == list(STC)[5]:  # big_machine
            await master_vlookup_update(main_to="\nΔ цена\n")
        else:
            await master_vlookup_update()
    else:
        print(f"Поставщик {supp} не найден в документе STC")


#  Переделать чтобы передавать только артикулы, без лишних данных
#  И убрать nan артикулы
async def common_tables_add_arts(
    upd: Message | CallbackQuery,
    n_data: list[dict[str, Any]],
    ws: Worksheet,
    table: str,
    supp: str,
):

    new_arts: list[str] = []
    if n_data:
        ex_arts_row = retryable()(
            lambda: ws.get(
                range_name="A3:A", value_render_option=ValueRenderOption.unformatted
            )
        )
        ex_arts: set[str] = {item[0] for item in ex_arts_row if item}
        new_lines: set[str] = (obj for obj in n_data if obj["art"] not in ex_arts)

        filtered_lines: list[dict[str, Any]] = []
        if table == list(STC)[0]:
            seas = (SeasonType.WINTER, SeasonType.ALLSEASON)
        elif table == list(STC)[1]:
            seas = (SeasonType.SUMMER,)
        for line in new_lines:
            if line["lt"] == "l" and line["seas"] in seas and notna(line["art"]):
                filtered_lines.append(line)

        if filtered_lines:

            sorted_stock: list[dict[str, Any]] = await sort_stock(filtered_lines)

            for line in sorted_stock:
                new_arts.append([line["art"]])

            msg_animation_1 = MessageAnimation(
                message_or_call=upd,
                base_text=f"<b>{table}</b> запись - создание пустых строк",
            )
            await msg_animation_1.start()

            retryable()(ws.add_rows)(len(new_arts) + 1)

            await msg_animation_1.stop()

            _l: str = BASE_LAYOUT["art"]["l"]

            msg_animation_2 = MessageAnimation(
                message_or_call=upd,
                base_text=f"<b>{table}</b> чтение - номер последней заполненной строки",
            )
            await msg_animation_2.start()

            number_last_row = retryable()(lambda: len(ws.col_values(1)) + 2)

            await msg_animation_2.stop()

            msg_animation_3 = MessageAnimation(
                message_or_call=upd,
                base_text=f"<b>{table}</b> запись - новых позиций",
            )
            await msg_animation_3.start()

            retryable()(ws.update)(new_arts, f"{_l}{number_last_row}")

            await msg_animation_3.stop()

            new_arts_amo: int = len(new_arts)

            msg_animation_4 = MessageAnimation(
                message_or_call=upd,
                base_text=f"<b>{table}</b> запись - количества и цены",
            )
            await msg_animation_4.start()

            #  19/11/2025
            _l: str = STC[table]["Последнее\nобновление"]["l"]
            retryable()(ws.update)(
                [[datetime.today().strftime("%d/%m/%Y")]] * new_arts_amo,
                f"{_l}{number_last_row}",
            )

            await msg_animation_4.stop()

    return new_arts
