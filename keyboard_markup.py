from aiogram.utils.keyboard import ReplyKeyboardBuilder
from own_utils import get_button


def main_menu_user():
    builder = ReplyKeyboardBuilder()
    builder.button(text=get_button("balance"))
    builder.button(text=get_button("top"))
    builder.button(text=get_button("history_transfer"))
    builder.adjust(2, 1)
    return builder.as_markup(
        resize_keyboard=True, input_field_placeholder="Бог тебя любит ♡"
    )


def main_menu_admin():
    builder = ReplyKeyboardBuilder()
    builder.button(text=get_button("statistics"))
    builder.button(text=get_button("delete_history_reason"))
    builder.button(text=get_button("top"))
    builder.button(text=get_button("items"))
    builder.button(text=get_button("flownomika"))
    builder.button(text=get_button("options_for_admin"))
    builder.adjust(1, 2, 2, 1)
    return builder.as_markup(
        resize_keyboard=True, input_field_placeholder="Бог тебя любит ♡"
    )


def cancel():
    builder = ReplyKeyboardBuilder()
    builder.button(text=get_button("cancel"))
    return builder.as_markup(
        resize_keyboard=True, input_field_placeholder="Бог тебя любит ♡"
    )


def menu_options():
    builder = ReplyKeyboardBuilder()
    builder.button(text=get_button("hand_reg"))
    builder.button(text=get_button("mailing"))
    builder.button(text=get_button("notifications"))
    builder.button(text=get_button("display"))
    builder.button(text=get_button("presets"))
    builder.button(text=get_button("back"))
    builder.adjust(1, 2, 2)
    return builder.as_markup(
        resize_keyboard=True, input_field_placeholder="Бог тебя любит ♡"
    )
