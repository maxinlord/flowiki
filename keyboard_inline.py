from aiogram.utils.keyboard import InlineKeyboardBuilder
from own_utils import get_button, get_table_name, get_text, weekday_tr
from tool_classes import Items, Preset


def keyboard_for_rule(id_user):
    builder = InlineKeyboardBuilder()

    builder.button(text=get_button("admin"), callback_data=f"rule:admin:{id_user}")
    builder.button(text=get_button("user"), callback_data=f"rule:user:{id_user}")
    builder.button(text=get_button("viewer"), callback_data=f"rule:viewer:{id_user}")
    builder.button(text=get_button("ban"), callback_data=f"rule:ban:{id_user}")
    builder.button(
        text=get_button("repeat_fio"), callback_data=f"action:repeat_fio:{id_user}"
    )

    builder.adjust(3, 2)
    return builder.as_markup()


def confirm_repeat_fio():
    builder = InlineKeyboardBuilder()

    builder.button(
        text=get_button("enter_repeat"), callback_data="action:enter_repeat_fio"
    )
    return builder.as_markup()


def confirm_reg_user():
    builder = InlineKeyboardBuilder()

    builder.button(text=get_button("end_reg"), callback_data="action:confirm_reg:user")
    return builder.as_markup()


def confirm_reg_viewer():
    builder = InlineKeyboardBuilder()

    builder.button(
        text=get_button("end_reg"), callback_data="action:confirm_reg:viewer"
    )
    return builder.as_markup()


def confirm_reg_admin():
    builder = InlineKeyboardBuilder()

    builder.button(text=get_button("end_reg"), callback_data="action:confirm_reg:admin")
    return builder.as_markup()


def flownomika_menu(side: str = "+"):
    builder = InlineKeyboardBuilder()
    emoji_plus = "🔘" if side == "+" else ""
    emoji_minus = "🔘" if side == "-" else ""
    num1 = get_button("num1")
    num2 = get_button("num2")
    num3 = get_button("num3")
    builder.button(
        text=get_button("another_quantity"),
        callback_data=f"action:enter_another_quantity:{side}",
    )
    builder.button(
        text=f"{side}{num1}", callback_data=f"action:select_num:{side}{num1}"
    )
    builder.button(
        text=f"{side}{num2}", callback_data=f"action:select_num:{side}{num2}"
    )
    builder.button(
        text=f"{side}{num3}", callback_data=f"action:select_num:{side}{num3}"
    )
    builder.button(
        text=get_button("menu_plus", throw_data={"emoji": emoji_plus}),
        callback_data="action:select_side:+",
    )
    builder.button(
        text=get_button("menu_minus", throw_data={"emoji": emoji_minus}),
        callback_data="action:select_side:-",
    )
    builder.adjust(1, 3, 2)
    return builder.as_markup()


def flownomika_list_users(
    list_users: list,
    size_one_page: int = 5,
    page_num: int = 1,
    is_many_selects: bool = False,
):
    builder = InlineKeyboardBuilder()
    grid_size = 0
    for num, user in enumerate(list_users):
        user: dict
        if (size_one_page * page_num) - size_one_page <= num < size_one_page * page_num:
            emoji = "🔘" if user["select"] else ""
            builder.button(
                text=get_button(
                    "pattern_line_button_user",
                    throw_data={
                        "fio": user["fio"],
                        "emoji": emoji,
                        "balance_flow": user["balance_flow"],
                    },
                ),
                callback_data=f"action:select_user:{user['id']}:{user['select']}",
            )
            grid_size += 1
    if is_many_selects:
        builder.button(
            text=get_button("end_choise"),
            callback_data="action:end_choise_selects",
        )
    else:
        builder.button(
            text=get_button("many_selects"), callback_data="action:many_selects"
        )
    builder.button(
        text=get_button("arrow_left"), callback_data=f"action:turn_left:{page_num}"
    )
    builder.button(
        text=get_button("arrow_right"), callback_data=f"action:turn_right:{page_num}"
    )
    builder.adjust(*[1 for _ in range(grid_size)], 1, 2)
    return builder.as_markup()


def get_files_k():
    table_names = get_table_name()
    builder = InlineKeyboardBuilder()
    for table in table_names["name"]:
        builder.button(text=table, callback_data=f"name_table:{table}")
    builder.adjust(1)
    return builder.as_markup()


def for_what():
    builder = InlineKeyboardBuilder()
    builder.button(text=get_button("for_what"), callback_data="action:ask:for_what")
    return builder.as_markup()


def arrows(page_num):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=get_button("arrow_left"), callback_data=f"action:to_left:{page_num}"
    )
    builder.button(
        text=get_button("arrow_right"), callback_data=f"action:to_right:{page_num}"
    )
    return builder.as_markup()


def menu_presets(user_presets):
    builder = InlineKeyboardBuilder()
    for preset in user_presets:
        emoji = "✅" if preset["is_active"] else ""
        builder.button(
            text=get_button(
                "pattern_name_preset",
                throw_data={"name_preset": preset["name_preset"], "emoji": emoji},
            ),
            callback_data=f"action:tap_on_preset:{preset['id_preset']}",
        )
    builder.button(
        text=get_button("add_new_preset"),
        callback_data="action:add_new_preset",
    )
    builder.adjust(1)
    return builder.as_markup()


def set_or_del_preset():
    builder = InlineKeyboardBuilder()
    builder.button(
        text=get_button("set_preset"),
        callback_data="action:set_preset",
    )
    builder.button(
        text=get_button("del_preset"),
        callback_data="action:del_preset",
    )
    builder.adjust(2)
    return builder.as_markup()


def presets_list_users(
    list_users: list,
    size_one_page: int = 5,
    page_num: int = 1,
):
    builder = InlineKeyboardBuilder()
    grid_size = 0
    for num, user in enumerate(list_users):
        user: dict
        if (size_one_page * page_num) - size_one_page <= num < size_one_page * page_num:
            emoji = "🔘" if user["select"] else ""
            builder.button(
                text=get_button(
                    "pattern_line_button_user",
                    throw_data={
                        "fio": user["fio"],
                        "emoji": emoji,
                        "balance_flow": user["balance_flow"],
                    },
                ),
                callback_data=f"action:preset_select_user:{user['id']}:{user['select']}",
            )
            grid_size += 1
    builder.button(
        text=get_button("by_default"),
        callback_data="action:by_default",
    )
    builder.button(
        text=get_button("end_choise"),
        callback_data="action:preset_end_choise_selects",
    )
    builder.button(
        text=get_button("arrow_left"),
        callback_data=f"action:preset_turn_left:{page_num}",
    )
    builder.button(
        text=get_button("arrow_right"),
        callback_data=f"action:preset_turn_right:{page_num}",
    )
    builder.adjust(*[1 for _ in range(grid_size)], 2, 2)
    return builder.as_markup()


def set_display(select: str = "-"):
    builder = InlineKeyboardBuilder()
    emoji_dsn = "✅" if select == "display_sername_name" else ""
    emoji_dns = "✅" if select == "display_name_sername" else ""
    builder.button(
        text=get_button("display_sername_name", throw_data={"emoji": emoji_dsn}),
        callback_data="action:set:display_sername_name",
    )
    builder.button(
        text=get_button("display_name_sername", throw_data={"emoji": emoji_dns}),
        callback_data="action:set:display_name_sername",
    )
    builder.adjust(1)
    return builder.as_markup()


def menu_notifications(user_notifications, id_user):
    type_notify = {
        'once':get_text('type_notify_once'),
        'remind':get_text('type_notify_remind')
    }
    builder = InlineKeyboardBuilder()
    for notify in user_notifications:
        preset = Preset(id_user)
        preset.id_preset = notify['id_preset']
        type_n = type_notify[notify['type_notify']]
        time = ' '.join(notify["time"].split()[::-1]) if notify['type_notify'] == 'once' else notify['time']
        builder.button(
            text=get_button(
                "pattern_notify", throw_data={"type_notify": type_n, "time_notify": time, 'weekday': weekday_tr[notify['weekday']], 'preset': preset.name_preset}
            ),
            callback_data=f"action:tap_on_notify:{notify['id_notify']}",
        )
    builder.button(
        text=get_button("add_new_notify"),
        callback_data="action:add_new_notify",
    )
    builder.adjust(1)
    return builder.as_markup()


def back_and_del_notify():
    builder = InlineKeyboardBuilder()
    builder.button(
        text=get_button("del_notify"),
        callback_data="action:del_notify",
    )
    builder.button(
        text=get_button("back_to_menu_notifications"),
        callback_data="action:back_to_menu_notifications",
    )

    builder.adjust(1)
    return builder.as_markup()


def menu_presets_for_notify(user_presets):
    builder = InlineKeyboardBuilder()
    for preset in user_presets:
        builder.button(
            text=get_button(
                "pattern_name_preset_for_notify",
                throw_data={"name_preset": preset["name_preset"]},
            ),
            callback_data=f"action:tap_on_preset:{preset['id_preset']}",
        )
    builder.button(
        text=get_button("base_preset_for_notify"),
        callback_data="action:tap_on_preset:base_preset",
    )
    builder.adjust(1)
    return builder.as_markup()


weekday_tr = {
    "monday": "Понедельник",
    "tuesday": "Вторник",
    "wednesday": "Среда",
    "thursday": "Четверг",
    "friday": "Пятница",
    "saturday": "Суббота",
    "sunday": "Воскресенье",
}


def week_days():
    builder = InlineKeyboardBuilder()
    for day in weekday_tr:
        builder.button(
            text=get_button(
                "pattern_name_day_for_notify",
                throw_data={"name_day": weekday_tr[day]},
            ),
            callback_data=f"action:tap_on_day:{day}",
        )
    builder.adjust(2)
    return builder.as_markup()


def type_notify():
    builder = InlineKeyboardBuilder()
    types = {
        "once": "Одноразово",
        "remind": "Напоминание",
    }
    for type_ in types:
        builder.button(
            text=get_button(
                "pattern_name_type_for_notify",
                throw_data={"name_type": types[type_]},
            ),
            callback_data=f"action:tap_on_type:{type_}",
        )
    builder.adjust(1)
    return builder.as_markup()


def menu_reason(reasons, page_num: int = 1, size_one_page: int = 9):
    builder = InlineKeyboardBuilder()
    grid_size = 0
    for ind, reason in enumerate(reasons):
        if (size_one_page * page_num) - size_one_page <= ind < size_one_page * page_num:
            emoji = "🔘" if reason["is_choose"] else ""
            builder.button(
                text=get_button(
                    "pattern_name_reason",
                    throw_data={
                        "emoji": emoji,
                        "date": reason["date"],
                        "sername": reason["name"],
                        "part_of_reason": reason["reason"][:7],
                        "num": reason["num"],
                    },
                ),
                callback_data=f"action:select_reason:{reason['tag']}",
            )
            grid_size += 1
    builder.button(
        text=get_button(
            "delete_reason",
        ),
        callback_data="action:delete_reason",
    )
    l = len(reasons)
    if l > 0:
        builder.button(
            text=get_button("arrow_left"),
            callback_data=f"action:history_to_del_turn_left:{page_num}",
        )
        builder.button(
            text=get_button("arrow_right"),
            callback_data=f"action:history_to_del_turn_right:{page_num}",
        )
        builder.adjust(*[1 for _ in range(grid_size)], 1, 2)
    else:
        builder.adjust(1)
    return builder.as_markup()


"{date} {sername} {part_of_reason}"


def menu_items(size_one_page: int = 5,
    page_num: int = 1,):
    builder = InlineKeyboardBuilder()
    items = Items()
    grid_size = []
    for num, item in enumerate(items):
        if (size_one_page * page_num) - size_one_page <= num < size_one_page * page_num:
            builder.button(
                text=get_button(
                    "pattern_button_inline_item",
                    throw_data={
                        "name": item["name"], 
                        'price':item['price']
                    },
                ),
                callback_data=f"action:tap_on_item:{item['id']}",
            )
            grid_size.append(1)
    if len(items) > size_one_page:
        builder.button(
            text=get_button("arrow_left"),
            callback_data=f"action:item_turn_left:{page_num}",
        )
        builder.button(
            text=get_button("arrow_right"),
            callback_data=f"action:item_turn_right:{page_num}",
        )
        grid_size.append(2)
    builder.button(
        text=get_button(
            "add_item",
        ),
        callback_data="action:add_item",
    )
    builder.adjust(*grid_size, 1)        
    
    return builder.as_markup()


def option_item():
    builder = InlineKeyboardBuilder()
    builder.button(
        text=get_button("edit_price"),
        callback_data="action:edit_price",
    )
    builder.button(
        text=get_button("edit_quantity"),
        callback_data="action:edit_quantity",
    )
    builder.button(
        text=get_button("reset_old_price"),
        callback_data="action:reset_old_price",
    )
    builder.button(
        text=get_button("get_qr_code"),
        callback_data="action:get_qr_code",
    )
    builder.button(
        text=get_button("del_item"),
        callback_data="action:del_item",
    )
    builder.button(
        text=get_button("back"),
        callback_data="action:back_to_menu_item",
    )
    builder.adjust(1, 1, 1, 3)
    return builder.as_markup()


def skip_photo():
    builder = InlineKeyboardBuilder()
    builder.button(
        text=get_button("skip_photo"),
        callback_data="action:skip_photo",
    )
    return builder.as_markup()


def buy_item_user(who, id_item):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=get_button("buy_item"),
        callback_data=f"action:buy_item_user:{who}:{id_item}",
    )
    return builder.as_markup()


def buy_item_admin(id_item):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=get_button("buy_item"),
        callback_data=f"action:buy_item_admin:{id_item}",
    )
    return builder.as_markup()


def buy_item_list_users(
    list_users: list,
    size_one_page: int = 5,
    page_num: int = 1,
):
    builder = InlineKeyboardBuilder()
    grid_size = 0
    for num, user in enumerate(list_users):
        user: dict
        if (size_one_page * page_num) - size_one_page <= num < size_one_page * page_num:
            builder.button(
                text=get_button(
                    "pattern_line_button_user_buy_item",
                    throw_data={
                        "fio": user["fio"],
                        "balance_flow": user["balance_flow"],
                    },
                ),
                callback_data=f"action:buy_item_select_user:{user['id']}",
            )
            grid_size += 1
    builder.button(
        text=get_button("arrow_left"),
        callback_data=f"action:buy_item_turn_left:{page_num}",
    )
    builder.button(
        text=get_button("arrow_right"),
        callback_data=f"action:buy_item_turn_right:{page_num}",
    )
    builder.adjust(*[1 for _ in range(grid_size)], 2)
    return builder.as_markup()


def mail_list_users(
    list_users: list,
    size_one_page: int = 5,
    page_num: int = 1,
):
    builder = InlineKeyboardBuilder()
    grid_size = 0
    for num, user in enumerate(list_users):
        user: dict
        if (size_one_page * page_num) - size_one_page <= num < size_one_page * page_num:
            emoji = "🔘" if user["select"] else ""
            builder.button(
                text=get_button(
                    "pattern_line_button_user_mail",
                    throw_data={"fio": user["fio"], "emoji": emoji},
                ),
                callback_data=f"action:mail:{user['id']}",
            )
            grid_size += 1
    builder.button(
        text=get_button("end_choise_user_mail"),
        callback_data="action:end_choise_user_mail",
    )
    builder.button(
        text=get_button("arrow_left"),
        callback_data=f"action:mail_turn_left:{page_num}",
    )
    builder.button(
        text=get_button("arrow_right"),
        callback_data=f"action:mail_turn_right:{page_num}",
    )
    builder.adjust(*[1 for _ in range(grid_size)], 1, 2)
    return builder.as_markup()
