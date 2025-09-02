from typing import Any

from aiogram.types import Message, CallbackQuery

from ..sheets import _sh, get_ws, STC
from ..sheets.fresh_stock import add_fresh_items
from ..sheets.fresh_amounts import add_fresh_amounts
from ..sheets.master_tables import common_tables_add_arts
from .file_utils import file_to_dict
from .json_4tochki_harvester import harv_4tochki
from .xls_olta_harvester import harv_olta


async def divide_by_key(data: list, param: str) -> dict:
    """Проходит по списку словарей, находит уникальные значения ключа {param}\n
    и составляет словарь с ключами из этих уникальных значений.\n
    После добавляет каждый словарь из начального списка в список, ключом которого является значение его параметра.
    """

    stock_by_param: dict = {}
    for i in data:
        key = i.get(param, "-")
        stock_by_param.setdefault(key, []).append(i)
    return stock_by_param


async def squeeze(upd: Message | CallbackQuery, msg_w_file: Message, supplier: str):
    """**The Very MAIN Function**

    Swallows the **price** file from a supplier and spits out lines of clean data straight to the table.\n
    Uses all the rest of data processing functions along the way.

    :param upd: An update that triggered the function.
    :param msg_w_file: Message containing the file.
    :param supplier: name of the supplier, which is also the name of the table.
    """
    _sh.worksheets()  # to keep the connection alive

    msg_1: str = f"✔︎  (<code>{supplier}</code>) Файл получен.\n"
    msg_2: str = "⇢  Начинаю обработку"

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

    data: dict[str, list[dict[str, Any]]] | list[dict[str, Any]] = await file_to_dict(
        msg=msg_w_file, supplier=supplier
    )
    ws = await get_ws(supplier)

    if supplier == list(STC)[2]:  # 4tochki
        validated_stock: dict[str, Any] = await harv_4tochki(data=data, ws=ws)
        msg_5: str = "позиций не прошли валидацию.\n"
    elif supplier == list(STC)[3]:
        validated_stock: dict[str, Any] = await harv_olta(data=data, ws=ws)
        print(f"Data len {validated_stock["i_data"]}")
        print(f"New_data len {len(validated_stock["new_data"])}")
        print(f"Amo_data len {len(validated_stock["amo_data"])}")
        print(f"Unvalidated len {len(validated_stock["unvalidated_lines"])}")

    msg_3 = f"✔︎  (<code>{msg_w_file.document.file_name}</code>) Файл провалидирован.\n"
    if len(validated_stock["unvalidated_lines"]) == 0:
        msg_4 = f"✔︎  Все <b>{validated_stock["i_data"]}</b> "
        msg_5: str = "строк прошли валидацию.\n"
    else:
        msg_4 = f"❍  <b>{len(validated_stock['unvalidated_lines'])}</b> из <b>{validated_stock["i_data"]}</b> "
        msg_5: str = "строк не прошли валидацию.\n"
    msg_6: str = f"❍  <b>{len(validated_stock["new_data"])}</b> новых позиций.\n"

    msg_8: str = "⇢  Добавляю провалидированные позиции."  # В табл ...

    msg_10: str = "⇢  Обновляю остатки."

    if validated_stock["new_data"]:

        msg = msg_1 + msg_3 + msg_4 + msg_5 + msg_6 + msg_8
        await upd.bot.edit_message_text(
            msg,
            chat_id=ch_id,
            message_id=msg_id,
        )

        # Добавляем позиции в табл. поставщика
        new_lines = await add_fresh_items(
            stock=validated_stock["new_data"], ws=ws, supp=supplier
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
        msg_7 = f"❍  <b>{len(validated_stock["new_data"])}</b> новых позиций. Добавлять нечего.\n"
        mes = msg_1 + msg_3 + msg_4 + msg_5 + msg_7
        await upd.bot.edit_message_text(
            text=mes + msg_10,
            chat_id=ch_id,
            message_id=msg_id,
        )

    #  Обновляем остатки в табл. поставщика
    await add_fresh_amounts(stock=validated_stock["amo_data"], ws=ws, supp=supplier)

    msg_11: str = f"✔︎  <b>Остатки обновлены</b> в таблице (<code>{supplier}</code>).\n"
    mes = mes + msg_11
    await upd.bot.edit_message_text(
        text=mes,
        chat_id=ch_id,
        message_id=msg_id,
    )

    if validated_stock["new_data"]:
        for table in list(STC)[:2]:
            msg_12: str = (
                f"⇢  Добавляю новые артикулы в таблицу (<code>{table}</code>).\n"
            )
            msg = mes + msg_12
            await upd.bot.edit_message_text(
                msg,
                chat_id=ch_id,
                message_id=msg_id,
            )

            ws = await get_ws(table)

            #  Добавляем новые артикулы на 2 главных страницы
            new_arts: list[str] = await common_tables_add_arts(
                n_data=validated_stock["new_data"],
                ws=ws,
                table=table,
                supp=supplier,
            )
            if new_arts:
                msg_13: str = (
                    f"✔︎  <b>{len(new_arts)}</b> новых строк добавлены в таблицу (<code>{table}</code>).\n"
                )
                mes = mes + msg_13
                await upd.bot.edit_message_text(
                    mes,
                    chat_id=ch_id,
                    message_id=msg_id,
                )
            else:
                msg_14: str = f"✔︎  В таблицу (<code>{table}</code>) добавить нечего.\n"
                mes = mes + msg_14
                await upd.bot.edit_message_text(
                    mes,
                    chat_id=ch_id,
                    message_id=msg_id,
                )
    else:
        msg_14: str = "✔︎  В главных таблицах нет недостоющих артикулов"
        mes = mes + msg_14
        await upd.bot.edit_message_text(
            mes,
            chat_id=ch_id,
            message_id=msg_id,
        )
