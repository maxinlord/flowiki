from aiogram import F
from own_utils import (
    activate_preset,
    count_page,
    create_tag_for_preset,
    de_active_presets,
    delete_preset,
    get_button,
    get_dict_users,
    get_text,
    set_preset,
    update_dict_users,
    wrap_2dd,
)
from dispatcher import main_router, bot
import keyboard_inline, keyboard_markup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from init_db import flow_db
from state_classes import Admin


@main_router.message(Admin.main, F.text == get_button("presets"))
async def presets_for_admin(message: Message, state: FSMContext) -> None:
    user_presets = flow_db.parse_2dd(
        table="users", key="presets", where="id", meaning=message.from_user.id
    )
    await state.update_data(user_presets=user_presets)
    await message.answer(
        text=get_text("menu_presets"),
        reply_markup=keyboard_inline.menu_presets(user_presets),
    )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "tap_on_preset",
)
async def tap_on_preset(query: CallbackQuery, state: FSMContext) -> None:
    id_preset = query.data.split(":")[-1]
    await state.update_data(selected_preset=id_preset)
    await bot.edit_message_reply_markup(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.set_or_del_preset(),
    )




@main_router.callback_query(
    Admin.main, F.data.split(":")[0] == "action", F.data.split(":")[1] == "set_preset"
)
async def process_set_preset(query: CallbackQuery, state: FSMContext) -> None:
    # sourcery skip: use-named-expression
    data = await state.get_data()
    id_preset = data["selected_preset"]
    user_presets = data["user_presets"]
    user_presets = de_active_presets(data["user_presets"])
    user_presets = activate_preset(user_presets, id_preset)
    await state.update_data(user_presets=user_presets)
    set_preset(id_user=query.from_user.id, id_preset_to_activate=id_preset)
    await bot.edit_message_reply_markup(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.menu_presets(user_presets),
    )


@main_router.callback_query(
    Admin.main, F.data.split(":")[0] == "action", F.data.split(":")[1] == "del_preset"
)
async def del_preset(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    id_preset = data["selected_preset"]
    user_presets = data["user_presets"]
    user_presets = delete_preset(user_presets, id_preset)
    await state.update_data(user_presets=user_presets)
    flow_db.delete_2dd(
        table="users",
        key="presets",
        where="id",
        meaning=query.from_user.id,
        unique_value_data=id_preset,
    )
    await bot.edit_message_reply_markup(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.menu_presets(user_presets),
    )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "add_new_preset",
)
async def add_new_preset(query: CallbackQuery, state: FSMContext) -> None:
    await bot.delete_message(
        message_id=query.message.message_id,
        chat_id=query.from_user.id,
    )
    await bot.send_message(
        text=get_text("enter_preset_name"),
        chat_id=query.from_user.id,
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(Admin.enter_name_preset)


@main_router.message(Admin.enter_name_preset)
async def get_name_presets(message: Message, state: FSMContext) -> None:
    name_preset = wrap_2dd(message.text)
    id_preset = create_tag_for_preset()
    d_users = get_dict_users()
    await state.update_data(
        d_users=d_users, id_preset=id_preset, page=1, name_preset=name_preset
    )
    await message.answer(
        text=get_text("choice_users_for_preset"),
        reply_markup=keyboard_inline.presets_list_users(d_users),
    )
    await state.set_state(Admin.main)


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "preset_turn_left",
)
async def preset_turn_left(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    q_page = count_page(5, len(data["d_users"]))
    if q_page == 1:
        return
    page = int(query.data.split(":")[-1].split(".")[0])
    page = page - 1 if page > 1 else q_page
    await state.update_data(page=page)
    await bot.edit_message_reply_markup(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.presets_list_users(
            list_users=data["d_users"],
            page_num=page,
        ),
    )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "preset_turn_right",
)
async def preset_turn_right(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    q_page = count_page(5, len(data["d_users"]))
    if q_page == 1:
        return
    page = int(query.data.split(":")[-1].split(".")[0])
    page = page + 1 if page < q_page else 1
    await state.update_data(page=page)
    await bot.edit_message_reply_markup(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.presets_list_users(
            list_users=data["d_users"],
            page_num=page,
        ),
    )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "preset_select_user",
)
async def preset_select_user(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    query_data = query.data.split(":")
    id_user = (
        query_data[2]
        if query_data[2] != "custom"
        else f"{query_data[2]}:{query_data[3]}"
    )
    d_users = update_dict_users(id_user, data["d_users"])
    await state.update_data(d_users=d_users)
    await bot.edit_message_reply_markup(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.presets_list_users(
            list_users=d_users, page_num=data["page"]
        ),
    )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "preset_end_choise_selects",
)
async def preset_end_choise_selects(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    id_user = query.from_user.id
    if not [i for i in data["d_users"] if i["select"] != False]:
        return await query.answer(
            text=get_text("preset_no_one_choice"), show_alert=True
        )
    ids = wrap_2dd(",".join([i["id"] for i in data["d_users"]]))
    flow_db.add_2dd(
        table="users",
        key="presets",
        where="id",
        meaning=query.from_user.id,
        throw_data=[data["name_preset"], data["id_preset"], ids, 0],
    )
    await bot.edit_message_reply_markup(
        chat_id=id_user, message_id=query.message.message_id, reply_markup=None
    )
    await bot.send_message(
        chat_id=id_user,
        text=get_text("preset_created"),
        reply_markup=keyboard_markup.menu_options(),
    )

@main_router.callback_query(
    Admin.main, F.data.split(":")[0] == "action", F.data.split(":")[1] == "by_default"
)
async def process_set_preset_by_default(query: CallbackQuery, state: FSMContext) -> None:
    id_user = query.from_user.id
    d_users = get_dict_users()
    data = await state.get_data()
    data_ = [user for user in d_users if user["rule"] == "user"]
    ids = wrap_2dd(",".join([i["id"] for i in data_]))
    flow_db.add_2dd(
        table="users",
        key="presets",
        where="id",
        meaning=query.from_user.id,
        throw_data=[data["name_preset"], data["id_preset"], ids, 0],
    )
    await bot.edit_message_reply_markup(
        chat_id=id_user, message_id=query.message.message_id, reply_markup=None
    )
    await bot.send_message(
        chat_id=id_user,
        text=get_text("preset_created"),
        reply_markup=keyboard_markup.menu_options(),
    )