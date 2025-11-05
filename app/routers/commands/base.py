import asyncio

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from ...kbds import reply_buttons, inline_buttons
from ...sheets import STC
from ...sheets.fresh_amounts import fix_formulas
from ...sheets.transfer import move
from ..router_objects import AdminCheck, Supplier_Msg_Add


rtr = Router(name=__name__)


@rtr.message(AdminCheck(), CommandStart())
async def start_admin(message: Message):
    print("start_admin command received from user:", message.from_user.id)
    await message.answer(
        f"""
<b>Шалом, {message.from_user.full_name}!</b>

Эта версия бота может:
- Обновлять остатки товаров поставщиков в таблице, считывая их из Excel или JSON файлов.
    Поддерживаются следующие файлы:
    - <b>JSON</b> файл с расширением <code>.json</code> выгрузка из 4tochki.
    - <b>Excel</b> файл с расширением <code>.xls</code> из OLTA.
"""
    )


@rtr.message(CommandStart())
async def start(message: Message):
    print("start command received from user:", message.from_user.id)
    await message.answer(f"Salom, {message.from_user.full_name}!")


@rtr.message(Command("help"))
async def help(message: Message):
    print("help command received from user:", message.from_user.id)
    await message.answer(
        """
<b>Использование бота:</b>

- (Напишу когда будет готово)
"""
    )


@rtr.message(Command("test"))
async def test(message: Message):
    print("test command received from user:", message.from_user.id)
    await message.answer("Test command received ✅")
    # await message.answer(f"Message ID: {message.message_id}")
    await asyncio.sleep(5)
    await message.bot.edit_message_text(
        text="Test command finished ✅",
        chat_id=message.chat.id,
        message_id=message.message_id + 1,
    )


@rtr.message(Command("rm_kb"))
async def rm_kb(message: Message):
    print("rm_kb command received from user:", message.from_user.id)
    await message.answer("Keyboard removed ✅", reply_markup=ReplyKeyboardRemove())


# @rtr.message(Command("mv"))
async def mv(message: Message):
    """
    I used this one that one time when I had to move handwritten columns from an old sheet to a new one.
    """
    pass


# SUPPLIERS STOCK ADD


@rtr.message(AdminCheck(), Command("add"))
async def add_stock(message: Message, state: FSMContext) -> None:
    """Small command, that routs to correct supplier stock harvester.\n

    This is a simple example of how to use aiogram callback data factory.\n
    - buttons are created dynamically based on the list of suppliers.
    - each button is an instance of the `Supplier` class, which packs its data for callback.
    """
    print("add_stock command received from user:", message.from_user.id)
    await state.clear()

    buttons: dict[str, str] = {}
    #  Берём названия поставщиков (supp: str) из STC
    for supp in list(STC)[2:]:
        #  Создаём экземпляр класса Supplier для каждого поставщика
        supp_cbq = Supplier_Msg_Add(name=supp)
        #  мы используем метод `pack()` для key и `name` для value
        buttons[supp_cbq.pack()] = supp
    #  inline_buttons обрабатывает данные в формате (buttons = {callback_data: button_text})
    i_kb = await inline_buttons(buttons=buttons, columns=2)
    await message.answer("<b>Чей прайс обновляем?</b>", reply_markup=i_kb)
