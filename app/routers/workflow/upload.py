from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery


from ..router_objects import (
    AdminCheck,
    Supplier_File_Add,
    Supplier_Msg_Add,
    Supplier_Msg_State,
    Supplier_File_State,
)
from ...kbds import inline_buttons
from ...sheets import STC
from app.dicts.convert import squeeze


rtr = Router()


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
            f"Пожалуйста, отправьте прайс {supp} в формате Excel."
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
    await call.answer(f"Вы выбрали {callback_data.name}")

    await squeeze(upd=call, msg_w_file=msg_w_file, supplier=supplier)
