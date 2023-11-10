from aiogram.utils.keyboard import InlineKeyboardBuilder
from own_utils import get_button, get_table_name
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def keyboard_for_rule(id_user):
    builder = InlineKeyboardBuilder()

    builder.button(text=get_button("admin"), callback_data=f"rule:admin:{id_user}")
    builder.button(text=get_button("ban"), callback_data=f"rule:ban:{id_user}")
    builder.button(text=get_button("user"), callback_data=f"rule:user:{id_user}")
    builder.button(
        text=get_button("repeat_fio"), callback_data=f"action:repeat_fio:{id_user}"
    )

    builder.adjust(2, 1, 1)
    return builder.as_markup()


def confirm_repeat_fio():
    builder = InlineKeyboardBuilder()

    builder.button(
        text=get_button("enter_repeat"), callback_data="action:enter_repeat_fio"
    )
    return builder.as_markup()


def confirm_reg_user():
    builder = InlineKeyboardBuilder()

    builder.button(
        text=get_button("end_reg"), callback_data="action:confirm_reg:user"
    )
    return builder.as_markup()


def confirm_reg_admin():
    builder = InlineKeyboardBuilder()

    builder.button(
        text=get_button("end_reg"), callback_data="action:confirm_reg:admin"
    )
    return builder.as_markup()


def flownomika_menu(side="+"):
    builder = InlineKeyboardBuilder()
    emoji_plus = "🔘" if side == "+" else ""
    emoji_minus = "🔘" if side == "-" else ""
    num1 = get_button("num1", throw_data={"side": side})
    num2 = get_button("num2", throw_data={"side": side})
    num3 = get_button("num3", throw_data={"side": side})
    builder.button(
        text=get_button("another_quantity"),
        callback_data=f"action:enter_another_quantity:{side}",
    )
    builder.button(text=num1, callback_data=f"action:num:{side}10")
    builder.button(text=num2, callback_data=f"action:num:{side}20")
    builder.button(text=num3, callback_data=f"action:num:{side}30")
    builder.button(
        text=get_button("menu_plus", throw_data={"emoji": emoji_plus}),
        callback_data="action:select:+",
    )
    builder.button(
        text=get_button("menu_minus", throw_data={"emoji": emoji_minus}),
        callback_data="action:select:-",
    )
    builder.adjust(1, 3, 2)
    return builder.as_markup()


def flownomika_list_users(
    list_users: list,
    size_one_page: int = 5,
    page_num: int = 1,
    many_selects: bool = False,
):
    builder = InlineKeyboardBuilder()
    grid_size = 0
    for num, user in enumerate(list_users):
        user: dict
        if (size_one_page * page_num) - size_one_page <= num < size_one_page * page_num:
            emoji = "🔘" if user['select'] else ""
            builder.button(
                text=get_button("pattern_line_button_user", throw_data={"name": user['name'],
                                                                    'emoji':emoji,
                                                                    'balance': user['balance']}),
                callback_data=f"action:select_user:{user['name']}:{user['select']}",
            )
            grid_size+=1
    if many_selects:
        builder.button(
            text=get_button("end_choise"),
            callback_data="action:end_choise_selects",
        )
    else:
        builder.button(
            text=get_button("many_selects"), callback_data="action:many_selects"
        )
    builder.button(text=get_button("arrow_left"), callback_data=f"action:turn_left:{page_num}")
    builder.button(
        text=get_button("arrow_right"), callback_data=f"action:turn_right:{page_num}"
    )
    # q_users = len(list_users) 
    # len_users = q_users if q_users <= size_one_page else size_one_page + (q_users - size_one_page * page_num)
    builder.adjust(*[1 for _ in range(grid_size)], 1, 2)
    return builder.as_markup()

def get_files_k():
    table_names = get_table_name()
    builder = InlineKeyboardBuilder()
    for table in table_names['name']:  
        builder.button(text=table, callback_data=f'name_table:{table}')
    builder.adjust(1)
    return builder.as_markup()

