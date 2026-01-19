import asyncio
from aiogram import Router, F
from aiogram.filters.command import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery


from app.routers.router_objects import AdminCheck
from app.dicts.names import BRANDS, MODELS
from app.dicts.matches_edit import (
    json_to_dict,
    add_name_to_matches,
    add_brand_to_matches,
    remove_name_from_matches,
)
from app.kbds import inline_buttons
from app.services.message_animation import MessageAnimation
from app.sheets import sh


rtr = Router(name=__name__)


class NamesEditingStates(StatesGroup):
    match_brand = State()
    add_match = State()
    rm_match = State()


class EditModels(CallbackData, prefix="edit_models"):
    button: str


class EditBrands(CallbackData, prefix="edit_brands"):
    button: str


#  -------------  Brands Editing  -------------  #


@rtr.message(AdminCheck(), Command("brands"))
async def list_brands_hand(message):
    brands = json_to_dict("brand_matches.json")

    #  Формируем текст ответа
    text = ""
    for k, v in brands.items():
        text += f"{k} -> {v}\n"

    await message.answer(
        f"Список брендов:\n{text}\n\n"
        # f"Чтобы отредактировать бренд, отправьте команду в формате:\n"
        # f"/edit_brand [старое_название];[новое_название]\n\n"
        # f"Пример:\n/edit_brand MICHELIN;MICHELIN_UPDATED"
    )


#  -------------  Models Editing  -------------  #


#  Read all the matches
@rtr.message(AdminCheck(), Command("matches"))
async def list_models_hand(message):
    models = json_to_dict("model_matches.json")

    text = ""
    #  Формируем текст ответа
    for k, v in models.items():
        text += f"<b>{k}</b>:\n"
        if isinstance(v, dict):
            for sk, sv in v.items():
                text += f"  {sk} -> {sv}\n"
        else:
            text += f"  {v}\n"  # На случай, если значение не словарь (ошибка в файле)

    await message.answer(f"Список моделей совпадений:\n{text}\n\n")


#
@rtr.message(AdminCheck(), Command("models"))
async def model_matches_hand(message: Message, state: FSMContext):

    await state.clear()
    await state.set_state(NamesEditingStates.match_brand)
    models = json_to_dict("model_matches.json")

    text = "\n".join(k for k in models.keys())

    await message.answer(
        f"Список существующих брендов в файле <i>model_matches.json</i>:\n\n{text}\n\n"
        "Введи бренд для которого хочешь отредактировать совпадения:\n"
        "<i>(или новый бренд для добавления)</i>"
    )


#
@rtr.message(NamesEditingStates.match_brand)
async def add_model_match_brand_hand(message: Message, state: FSMContext, prefix=""):

    await state.set_state(NamesEditingStates.match_brand)

    #  Проверяем, не вернулись ли мы в этот обработчик из добавления нового бренда
    go_back = await state.get_value("go_back")

    #  Получаем сохранённый бренд из состояния (если вернулись)
    #  Или из сообщения (если это первый вызов функции)
    brand_input = message.text.strip()
    if not go_back:
        await state.update_data(brand=brand_input)
    brand = await state.get_value("brand")

    #  После чего сбрасываем флаг возврата
    await state.update_data(go_back=False)

    matches = json_to_dict("model_matches.json")
    if brand not in matches.keys():

        buttons = {EditModels(button="add_brand").pack(): "Добавить этот бренд"}
        kbd = await inline_buttons(buttons=buttons, columns=2)

        await message.answer(
            f"{prefix}\n\n"
            "Такого бренда нет в списке совпадений.\n<b>Введи корректный бренд:</b>",
            reply_markup=kbd,
        )
        return
    else:
        brand_matches: str = "\n".join(
            f"{e}:{k}->{v}" for e, (k, v) in enumerate(matches[brand].items())
        )

        buttons = {
            EditModels(button="add_match").pack(): "➕",
            EditModels(button="rm_match").pack(): "➖",
        }
        kbd = await inline_buttons(buttons=buttons, columns=2)

        await message.answer(
            (
                f"{prefix}\n"
                f"Текущие совпадения для бренда\n<b>{brand}</b>:\n{brand_matches}\n\n"
                "Что делаем?\n"
            ),
            reply_markup=kbd,
        )


#
@rtr.callback_query(
    AdminCheck(),
    EditModels.filter(F.button == "add_brand"),
    NamesEditingStates.match_brand,
)
async def add_model_match_new_brand_hand(call: CallbackQuery, state: FSMContext):
    brand = await state.get_value("brand")

    add_brand_to_matches(brand=brand)

    prefix: str = f"Бренд {brand} добавлен в <i>model_matches.json</i>.\n"

    await state.update_data(go_back=True)
    await add_model_match_brand_hand(call.message, state, prefix=prefix)


#
@rtr.callback_query(
    AdminCheck(),
    EditModels.filter(F.button == "add_match"),
    NamesEditingStates.match_brand,
)
async def add_model_match_new_match_hand(call: CallbackQuery, state: FSMContext):
    await state.set_state(NamesEditingStates.add_match)
    brand = await state.get_value("brand")

    await call.message.answer(
        f"Добавление нового совпадения для бренда <b>{brand}</b>.\n"
        "Введи новое совпадение в формате:\n"
        "&lt;сырое_капсом&gt;:&lt;нормальное&gt;"
    )


#
@rtr.message(AdminCheck(), NamesEditingStates.add_match)
async def add_model_match_hand(message: Message, state: FSMContext):
    match_input = message.text.strip()
    if ":" not in match_input:
        await message.answer(
            "Некорректный формат совпадения. Введи нормально:\n"
            "&lt;сырое_капсом&gt;:&lt;нормальное&gt;"
        )
        return

    raw_name, proper_name = map(str.strip, match_input.split(":", 1))
    brand = await state.get_value("brand")

    add_name_to_matches(raw_name=raw_name, proper_name=proper_name, brand=brand)

    await state.update_data(go_back=True)
    await add_model_match_brand_hand(message, state)


#
@rtr.callback_query(
    AdminCheck(),
    EditModels.filter(F.button == "rm_match"),
    NamesEditingStates.match_brand,
)
async def remove_model_match_button_hand(call: CallbackQuery, state: FSMContext):

    await state.set_state(NamesEditingStates.rm_match)

    await call.message.answer(
        ("Какой match удаляем?\n" "Введи номер совпадения из списка.")
    )


#
@rtr.message(AdminCheck(), NamesEditingStates.rm_match)
async def remove_model_match_hand(message: Message, state: FSMContext):
    index_input = message.text.strip()
    index = int(index_input)
    if not index_input.isdigit():
        await message.answer("Некорректный ввод. Введи номер совпадения из списка.")
        return

    brand = await state.get_value("brand")
    matches = json_to_dict("model_matches.json")

    if index < 0 or index >= len(matches[brand]):
        await message.answer("Такого номера нет в списке совпадений. Попробуй ещё раз.")
        return

    for i, model in enumerate(matches[brand]):
        print(i, model)
        if i == index:

            await state.update_data(model=model)
            buttons = {EditModels(button="confirm_rm").pack(): "Удалить"}
            kbd = await inline_buttons(buttons=buttons, columns=2)

            await message.answer(
                f"Совпадение:\n{i}: {model} -> {matches[brand][model]}\n\nУдаляем?",
                reply_markup=kbd,
            )
            break


#
@rtr.callback_query(
    AdminCheck(),
    EditModels.filter(F.button == "confirm_rm"),
    NamesEditingStates.rm_match,
)
async def confirm_remove_model_match_hand(call: CallbackQuery, state: FSMContext):
    brand = await state.get_value("brand")
    model = await state.get_value("model")
    remove_name_from_matches(raw_name=model, brand=brand)

    prefix: str = f"Совпадение {model} удалено из бренда {brand}.\n"

    await state.update_data(go_back=True)
    await add_model_match_brand_hand(call.message, state, prefix=prefix)


#  Редактировать совпадения бренда

#  Добавить совпадение для бренда

#  Отредактировать все совпадения внутри бренда


#  -------------  Google Sheets  -------------  #


@rtr.message(AdminCheck(), Command("sheets"))
async def list_sheets_hand(message):
    #  Вывести список доступных таблиц
    # print(f"Available sheets: {_sh.worksheets()}")
    olta = sh.worksheet("olta")
    arts = olta.col_values(1)
    number_last_row: int = len(olta.get("A3:A")) + 4
    for a in arts:
        print(a)

    print(len(arts))
    print(f"Last row number: {number_last_row}")


#  -------------  Test Message Animation  -------------  #


class MsgAnimation(CallbackData, prefix="test_msg_anim"):
    """Assembles inline keyboard of suppliers after user **types /add**"""

    name: str


@rtr.message(AdminCheck(), Command("animation"))
async def test_animation_hand(message: Message):

    mes = await message.answer("Это сообщение до анимации.")

    anim = MessageAnimation(
        message_or_call=message,
        base_text="Загружаю данные",
    )
    await anim.start()
    #  Симулируем длительную операцию
    await asyncio.sleep(15)
    await anim.stop()

    buttons = {
        MsgAnimation(name="next").pack(): "Прочитать",
    }
    kbd = await inline_buttons(buttons=buttons, columns=1)

    await mes.edit_text("Анимация завершена.", reply_markup=kbd)


@rtr.callback_query(AdminCheck(), MsgAnimation.filter(F.name == "next"))
async def test_animation_next_hand(call: CallbackQuery):
    await call.answer("Нажата кнопка OK после анимации.")

    mes = await call.message.answer("Это сообщение до анимации.")

    anim = MessageAnimation(
        message_or_call=call,
        base_text="Читаю данные",
    )
    await anim.start()
    #  Симулируем длительную операцию
    await asyncio.sleep(15)
    await anim.stop()

    await mes.edit_text("Анимация завершена.")
