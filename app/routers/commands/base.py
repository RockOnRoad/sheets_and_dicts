from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from ...kbds import inline_buttons
from app.sheets import STC

from ..router_objects import AdminCheck, Supplier_Msg_Add


rtr = Router(name=__name__)


@rtr.message(AdminCheck(), CommandStart())
async def start_admin(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"""
<b>Привет {message.from_user.full_name}!</b>

Эта версия бота может:
- Обновлять остатки товаров поставщиков в таблице, считывая их из Excel или JSON файлов.

  Поддерживаются следующие файлы:
Выгрузка 4tochki.
  - <b>JSON</b> файл с расширением (<b>.json</b>)
Прайс листы остальных поставщиков.
  - <b>Excel</b> файл с расширением (<b>.xls</b>) или (<b>.xlsx</b>).

Для загрузки документа используйте команду /add\nили отправьте файл напрямую в чат.
"""
    )


@rtr.message(AdminCheck(), Command("help"))
async def help_admin(message: Message, state: FSMContext):
    await state.clear()
    print("help command received from admin user:", message.from_user.id)
    suppliers = "\n".join(f"- {supp}" for supp in list(STC)[2:])
    await message.answer(
        f"""
Этот бот выполняет одну лишь функцию:
<b>Обновляет остатки товаров поставщиков в таблице Google Sheets.</b>

Доступные поставщики:
{suppliers}

Доступные команды:
/start - Приветствие и информация о возможностях бота.
/help - Показать это сообщение.
/add - Начать процесс добавления остатков товаров от поставщика.
"""
    )


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
        #  мы используем метод `pack()` для key и `name` для value
        buttons[Supplier_Msg_Add(name=supp).pack()] = supp
    #  inline_buttons обрабатывает данные в формате (buttons = {callback_data: button_text})
    i_kb = await inline_buttons(buttons=buttons, columns=2)
    await message.answer("<b>Чей прайс обновляем?</b>", reply_markup=i_kb)


@rtr.message(CommandStart())
async def start(message: Message):
    print("start command received from user:", message.from_user.id)
    await message.answer("Вы не авторизованы. Обратитесь к администратору.")


@rtr.message(Command("help"))
async def help(message: Message):
    print("help command received from user:", message.from_user.id)
    await message.answer("Вы не авторизованы. Обратитесь к администратору.")


@rtr.message(Command("add"))
async def add(message: Message, state: FSMContext) -> None:
    print("add command received from user:", message.from_user.id)
    await state.clear()
    await message.answer("Вы не авторизованы. Обратитесь к администратору.")


@rtr.message(Command("test"))
async def test(message: Message):
    pass


@rtr.message(Command("rm_kb"))
async def rm_kb(message: Message):
    await message.answer("Keyboard removed ✅", reply_markup=ReplyKeyboardRemove())
