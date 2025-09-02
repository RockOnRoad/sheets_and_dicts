import json
from random import randint
from typing import Any
from time import time

from io import BytesIO
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import asyncio

import pandas as pd  # type: ignore

from ..router_objects import (
    AdminCheck,
    Supplier_File_Add,
    Supplier_Msg_Add,
    Supplier_Msg_State,
    Supplier_File_State,
)
from ...kbds import inline_buttons
from ...sheets import STC, get_ws
from app.dicts.convert import divide_by_key, squeeze
from app.sheets.add_amounts import update_amounts
from app.sheets.add_rows import append_rows


rtr = Router()


# @rtr.message(AdminCheck(), F.document.file_name.endswith(".json"))
async def handle_json_file(message: Message) -> None:
    """Отлавливает json файлы, парсит их содержимое и добавляет это содержимое в таблицу."""

    key: str = "season"

    if not message.document.file_name.endswith(".json"):
        await message.reply("Только .json файлы поддерживаются.")
        return

    file_obj = BytesIO()
    await message.bot.download(message.document.file_id, destination=file_obj)
    file_obj.seek(0)

    try:
        data = json.load(file_obj)
    except Exception as e:
        file_obj.close()
        await message.reply(f"Ошибка при обработке файла: {str(e)}")
        return
    else:
        await message.answer(
            f"Файл <b>{message.document.file_name}</b> успешно загружен."
        )
        file_obj.close()

    only_tires: list = data["tires"]
    await message.answer(
        f"✅ Файл прочитан.\nКоличество позиций шин: <b>{len(only_tires)}</b>"
    )

    only_kryarsk2: list = [line for line in only_tires if "price_kryarsk2" in line]
    #  [{'cae': 'F7640', 'gtin': 02900077764912, 'name': '...'}, {'cae': 'F7641', 'a': 3, 'b': 4}, ...]
    await message.answer(
        f"✅ Количество позиций шин в наличии на складе Красноярск2: <b>{len(only_kryarsk2)}</b>"
    )

    #  >>>>>>>>>>>

    separorated_stock: dict = await divide_by_key(data=only_kryarsk2, param=key)
    #  {'Зимняя': [{'cae': 'F7640', 'name': ...}, {}, {}], 'Летняя': [{'cae': '2177000', {}, {}], ...}

    await message.answer(
        f"""✅ Позиции рассортированы по сезону.
{'\n'.join([f'{key} ({len(value)} строк)' for key, value in separorated_stock.items()])}"""
    )

    if key == "season":

        sheets = {
            # "Зимняя": "test"
            "Зимняя": "snow_4tochki",
            "Летняя": "summer_4tochki",
            "Всесезонная": "all_season_4tochki",
        }

        for item in sheets:
            ws = get_ws(sheets[item])

            await append_rows(sheet=ws, stock=separorated_stock[item], message=message)
            await message.answer(
                f"✅ Новые позиции добавлены в конец таблицы <b>{sheets[item]}</b>."
            )

            await update_amounts(sheet=ws, stock=only_kryarsk2, message=message)


# @rtr.message(AdminCheck(), F.document.file_name.endswith(".xls"))
async def handle_xls_file(message: Message) -> None:
    pass


# @rtr.message(F.document)
async def wrong_format(message: Message) -> None:
    await message.answer(
        "Допускаются только файлы форматов:\n`.json` для 4tochki\n`.xls` или '.xlsx` для olta и других поставщиков."
    )


# /ADD REPLIES


@rtr.callback_query(AdminCheck(), Supplier_Msg_Add.filter(F.name.in_(list(STC)[2:])))
async def reply_supp(
    call: CallbackQuery, callback_data: Supplier_Msg_Add, state: FSMContext
):
    """**Reply to the 4tochki stock upload request.**

    Both call.data and callback_data.name are strings, but they are used differently:

    :param call: is an Update Object like `Message`.
    Though instead of text it has `data` which is like this (call.data: str - 'supp_add:(some_name)')
    :param callback_data: is a container of data from the callback query, (callback_data.name: str - '4tochki').
    Also it helps understand which scenario is being executed.
    :param state: is for Finite State Machine (FSM) to keep track of the current state of the dialog.
    1 great thing about state is that, being a dictionary it can store any values with any names.
    """
    await state.clear()

    supp = callback_data.name
    await state.set_state(Supplier_Msg_State.add_command)
    await state.update_data(name=supp)

    await call.answer(f"Вы выбрали {supp}. Отправьте файл с выгрузкой.")
    if supp == list(STC)[2]:
        await call.message.edit_text(
            f"Пожалуйста, отправьте файл с выгрузкой из {supp} в формате `.json`."
        )
    elif supp in list(STC)[3:]:
        await call.message.edit_text(
            f"Пожалуйста, отправьте Excel файл с выгрузкой из {supp}."
        )
    else:
        await call.message.edit_text('<b>404</b> IMPUSIBRU !??"|')


# FILE /ADD


@rtr.message(AdminCheck(), Supplier_Msg_State.add_command, F.document)
async def harvest_file(message: Message, state: FSMContext):

    supplier: str = (await state.get_data())["name"]  # list(STC)[supplier]
    await state.clear()

    await squeeze(upd=message, msg_w_file=message, supplier=supplier)


#  File not sent (Exception)
@rtr.message(AdminCheck(), Supplier_Msg_State.add_command)
async def not_file(message: Message, state: FSMContext):
    """**Handles the case when a user sends a message that is not a file.**

    This function is triggered when the user sends a message while in the `add_command` state.
    It informs the user that they need to send a file and clears the state.

    :param message: The message object containing the user's input.
    :param state: The FSMContext object to manage the state of the conversation.
    """
    supplier: str = (await state.get_data())["name"]  # list(STC)[supplier]

    await message.answer(
        f"Я жду файл с выгрузкой из <b>{supplier}</b>, а не сообщение.\n"
    )


# FILE SENT


@rtr.message(AdminCheck(), F.document)
async def file_sent_no_context(message: Message, state: FSMContext):
    print(f"file {message.document.file_name} sent by user: {message.from_user.id}")
    await state.clear()

    await state.set_state(Supplier_File_State.file)
    await state.update_data(msg_w_file=message)

    buttons: dict[str, str] = {}
    for supp in list(STC)[2:]:
        supp_cbq = Supplier_File_Add(name=supp)
        buttons[supp_cbq.pack()] = supp
    i_kb = await inline_buttons(buttons=buttons, columns=2)
    await message.reply("Это от кого?", reply_markup=i_kb)


#  Supplier Chosen
@rtr.callback_query(
    AdminCheck(),
    Supplier_File_Add.filter(F.name.in_(list(STC)[2:])),
    Supplier_File_State.file,
)
async def file_sent_context(
    call: CallbackQuery, callback_data: Supplier_Msg_Add, state: FSMContext
):
    msg_w_file: Message = (await state.get_data())["msg_w_file"]
    await state.clear()

    supplier: str = callback_data.name
    await call.answer("Вы выбрали " + callback_data.name)

    await squeeze(upd=call, msg_w_file=msg_w_file, supplier=supplier)
