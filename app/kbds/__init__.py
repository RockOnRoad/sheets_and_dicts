from aiogram.filters.callback_data import CallbackData
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


async def reply_buttons(
    options: list[str] | tuple[str],
    placeholder_txt: str = "Type Command",
    adjst: int = 1,
) -> ReplyKeyboardMarkup:
    """**Assambles a `reply_keyboard`**

    :param options: List of names for reply buttons.
    :param placeholder_txt: Text that sits in an input field.
    :param adjst: Number of grid columns.
    :return: Reply Keyboard.

    """

    keyboard = ReplyKeyboardBuilder()
    for option in options:
        keyboard.button(text=option)
        keyboard.adjust(adjst)
    return keyboard.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder=placeholder_txt,
    )


async def inline_buttons(
    buttons: dict[str, str], columns: int = 2
) -> InlineKeyboardMarkup:
    """**Assambles an `inline_keyboard`**

    :param buttons: Dictionary where keys are `callback data` and values are `names` of inline buttons.
    :param columns: Number of grid columns.
    :return: Inline Keyboard.

    """
    inline_buttons = InlineKeyboardBuilder()
    # Распаковываем переданный словарь в текст и callback_data кнопок
    for cb_q, text in buttons.items():
        # Создаем кнопку с текстом и callback_data
        inline_buttons.button(text=f"{text}", callback_data=f"{str(cb_q)}")
    inline_buttons.adjust(columns)
    return inline_buttons.as_markup()
