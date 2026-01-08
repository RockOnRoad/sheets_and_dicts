from typing import Any

from aiogram.types import Message, CallbackQuery

from ..sheets import _sh, get_ws, STC
from ..sheets.fresh_stock import add_new_items
from ..sheets.fresh_amounts import add_fresh_amounts
from ..sheets.master_tables import common_tables_add_arts, fix_master_formulas
from .file_utils import file_handler


async def squeeze(upd: Message | CallbackQuery, msg_w_file: Message, supplier: str):
    """**The Very MAIN Function**

    Swallows **price** file from a supplier and spits out lines of clean data straight to the table.\n
    Uses all the rest of data processing functions along the way.

    :param upd: An update that triggered the function.
    :param msg_w_file: Message containing the file.
    :param supplier: name of the supplier, which is also the name of the table.
    """
    _sh.worksheets()  # to keep the connection alive

    msg_1: str = f"✔︎  Файл поставщика (<code>{supplier}</code>) получен.\n"
    msg_2: str = "⇢  Проверка"

    if isinstance(upd, Message):
        msg_id: int = upd.message_id + 1
        ch_id: int = upd.chat.id

        mes: str = msg_1 + msg_2
        await upd.answer((mes))

    elif isinstance(upd, CallbackQuery):
        msg_id = upd.message.message_id
        ch_id = upd.message.chat.id

        mes: str = msg_1 + msg_2
        await upd.message.edit_text((mes))

    ws = await get_ws(supplier)

    #  ------------  FILE UTILITY  ------------

    validated_stock: dict[str, Any] = await file_handler(
        msg=msg_w_file, supplier=supplier, ws=ws
    )

    msg_3 = f"✔︎  (<code>{msg_w_file.document.file_name}</code>) Файл провалидирован.\n"
    if len(validated_stock["trash_lines"]) == 0:
        msg_4 = f"✔︎  Все <b>{validated_stock["i_data"]}</b> "
    else:
        msg_4: str = (
            f"❍  <b>{len(validated_stock["new_lines"])}</b> из <b>{validated_stock["i_data"]}</b> "
        )
    msg_5: str = "новых позиций прошли валидацию.\n"
    msg_8: str = "⇢  Добавляю провалидированные позиции."  # В табл ...
    msg_10: str = "⇢  Обновляю остатки."

    if validated_stock["new_lines"]:

        msg = msg_1 + msg_3 + msg_4 + msg_5 + msg_8
        await upd.bot.edit_message_text(
            msg,
            chat_id=ch_id,
            message_id=msg_id,
        )

        # Добавляем позиции в табл. поставщика
        new_lines = await add_new_items(
            stock=validated_stock["new_lines"], ws=ws, supp=supplier
        )

        msg_9: str = (
            f"✔︎  <b>{len(new_lines)}</b> новых строк добавлены в таблицу <b>{supplier}</b>.\n"
        )
        mes = msg_1 + msg_3 + msg_4 + msg_5 + msg_9
        await upd.bot.edit_message_text(
            text=mes + msg_10,
            chat_id=ch_id,
            message_id=msg_id,
        )
    else:

        msg_7 = f"❍  <b>{len(validated_stock["new_lines"])}</b> новых позиций. Добавлять нечего.\n"
        mes = msg_1 + msg_3 + msg_4 + msg_5 + msg_7
        await upd.bot.edit_message_text(
            text=mes + msg_10,
            chat_id=ch_id,
            message_id=msg_id,
        )

    #  Обновляем остатки в табл. поставщика
    await add_fresh_amounts(stock=validated_stock["amo_data"], ws=ws, supp=supplier)

    msg_11: str = f"✔︎  <b>Остатки обновлены</b> в таблице <b>{supplier}</b>.\n"
    mes = mes + msg_11
    await upd.bot.edit_message_text(
        text=mes,
        chat_id=ch_id,
        message_id=msg_id,
    )

    for table in list(STC)[:2]:

        ws = await get_ws(table)

        if validated_stock["new_lines"]:
            msg_12: str = f"⇢  Добавляю новые артикулы в таблицу <b>{table}</b>.\n"
            msg = mes + msg_12
            await upd.bot.edit_message_text(
                msg,
                chat_id=ch_id,
                message_id=msg_id,
            )

            #  Добавляем новые артикулы на 2 главных страницы
            new_arts: list[str] = await common_tables_add_arts(
                n_data=validated_stock["new_lines"],
                ws=ws,
                table=table,
                supp=supplier,
            )

            if new_arts:
                msg_13: str = (
                    f"✔︎  <b>{len(new_arts)}</b> новых строк добавлены в таблицу <b>{table}</b>.\n"
                )
                mes = mes + msg_13
                await upd.bot.edit_message_text(
                    mes,
                    chat_id=ch_id,
                    message_id=msg_id,
                )
            else:
                msg_14: str = f"✔︎  В таблицу <b>{table}</b> добавить нечего.\n"
                mes = mes + msg_14
                await upd.bot.edit_message_text(
                    mes,
                    chat_id=ch_id,
                    message_id=msg_id,
                )

        await fix_master_formulas(ws=ws, table=table, supp=supplier)

    if validated_stock["new_lines"] == []:
        msg_14: str = "✔︎  В главных таблицах нет недостоющих артикулов"
        mes = mes + msg_14
        await upd.bot.edit_message_text(
            mes,
            chat_id=ch_id,
            message_id=msg_id,
        )
