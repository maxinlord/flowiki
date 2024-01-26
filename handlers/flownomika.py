from aiogram import F
from own_utils import (
    count_page,
    get_button,
    get_current_date,
    get_text,
    update_dict_users,
    view_selected_users,
    wrap,
    extract_date
)
from dispatcher import main_router, bot
import keyboard_inline, keyboard_markup
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import config

from state_classes import Admin
from tool_classes import MessageReason, Reason, User, Users


@main_router.message(Admin.main, F.text == get_button("flownomika"))
async def flownomika(message: Message, state: FSMContext) -> None:
    await state.update_data(
        side="+", num=None, is_many_selects=False, d_users=None, page=1
    )
    await message.answer(
        get_text(
            "flownomika_menu_1",
            throw_data={
                "side": get_text("side_+"),
                "num": get_text("no_quantity_to_add"),
                "l_users": get_text("no_choise_users"),
            },
        ),
        reply_markup=keyboard_inline.flownomika_menu(),
    )
    await state.set_state(Admin.main)


@main_router.callback_query(
    Admin.main, F.data.split(":")[0] == "action", F.data.split(":")[1] == "select_side"
)
async def process_select_side(query: CallbackQuery, state: FSMContext) -> None:
    side = query.data.split(":")[-1]
    await state.update_data(side=side)
    await bot.edit_message_text(
        text=get_text(
            "flownomika_menu_1",
            throw_data={
                "side": get_text(f"side_{side}"),
                "num": get_text("no_quantity_to_add"),
                "l_users": get_text("no_choise_users"),
            },
        ),
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.flownomika_menu(side),
    )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "enter_another_quantity",
)
async def process_enter_another_quantity(
    query: CallbackQuery, state: FSMContext
) -> None:
    side = query.data.split(":")[-1]
    await state.update_data(side=side)
    await query.message.delete()
    await query.message.answer(
        text=get_text("enter_another_quantity"),
        reply_markup=keyboard_markup.cancel(),
    )
    await state.set_state(Admin.enter_another_quantity)


@main_router.message(Admin.enter_another_quantity)
async def enter_another_quantity(message: Message, state: FSMContext) -> None:
    if message.text == get_button("cancel"):
        await state.set_state(Admin.main)
        await message.answer(
            text=get_text("canceled"), reply_markup=keyboard_markup.main_menu_admin()
        )
        return await flownomika(message, state)
    if not message.text.isnumeric():
        return
    data = await state.get_data()
    side = data["side"]
    d_users = Users(message.from_user.id).to_dict_for_keyboard
    await state.update_data(num=f"{side}{message.text}", d_users=d_users)
    await message.answer(
        get_text(
            "flownomika_menu_2",
            throw_data={
                "side": get_text(f"side_{side}"),
                "num": f"{side}{message.text}",
                "l_users": get_text("no_choise_users"),
                "cpage": wrap(1),
                "allpage": wrap(count_page(5, len(d_users))),
            },
        ),
        reply_markup=keyboard_inline.flownomika_list_users(d_users),
    )
    await state.set_state(Admin.main)


@main_router.callback_query(
    Admin.main, F.data.split(":")[0] == "action", F.data.split(":")[1] == "select_num"
)
async def process_select_num(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    num = query.data.split(":")[-1]
    side = data["side"]
    d_users = Users(query.from_user.id).to_dict_for_keyboard
    await state.update_data(num=num, d_users=d_users)
    await bot.edit_message_text(
        text=get_text(
            "flownomika_menu_2",
            throw_data={
                "side": get_text(f"side_{side}"),
                "num": num,
                "l_users": get_text("no_choise_users"),
                "cpage": wrap(1),
                "allpage": wrap(count_page(5, len(d_users))),
            },
        ),
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.flownomika_list_users(d_users),
    )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1].in_(["turn_left", "turn_right"]),
)
async def process_turn_left(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    side = data["side"]
    q_page = count_page(5, len(data["d_users"]))
    if q_page == 1:
        return
    page = int(query.data.split(":")[-1].split(".")[0])
    if query.data.split(":")[1] == "turn_left":
        page = page - 1 if page > 1 else q_page
    else:
        page = page + 1 if page < q_page else 1
    await state.update_data(page=page)
    await bot.edit_message_text(
        text=get_text(
            "flownomika_menu_2",
            throw_data={
                "side": get_text(f"side_{side}"),
                "num": data["num"],
                "l_users": view_selected_users(data["d_users"]),
                "cpage": wrap(page),
                "allpage": wrap(q_page),
            },
        ),
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.flownomika_list_users(
            list_users=data["d_users"],
            is_many_selects=data["is_many_selects"],
            page_num=page,
        ),
    )


@main_router.callback_query(
    Admin.main, F.data.split(":")[0] == "action", F.data.split(":")[1] == "many_selects"
)
async def process_many_selects(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await state.update_data(is_many_selects=True)
    await bot.edit_message_reply_markup(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.flownomika_list_users(
            list_users=data["d_users"], is_many_selects=True, page_num=data["page"]
        ),
    )


@main_router.callback_query(
    Admin.main, F.data.split(":")[0] == "action", F.data.split(":")[1] == "select_user"
)
async def process_select_user(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    query_data = query.data.split(":")
    side = data["side"]
    id_user = (
        query_data[2]
        if query_data[2] != "custom"
        else f"{query_data[2]}:{query_data[3]}"
    )
    d_users = update_dict_users(id_user, data["d_users"])
    await state.update_data(d_users=d_users)
    if data["is_many_selects"]:
        await bot.edit_message_text(
            text=get_text(
                "flownomika_menu_2",
                throw_data={
                    "side": get_text(f"side_{side}"),
                    "num": data["num"],
                    "l_users": view_selected_users(d_users),
                    "cpage": wrap(int(data["page"])),
                    "allpage": wrap(count_page(5, len(d_users))),
                },
            ),
            chat_id=query.from_user.id,
            message_id=query.message.message_id,
            reply_markup=keyboard_inline.flownomika_list_users(
                list_users=d_users, is_many_selects=True, page_num=data["page"]
            ),
        )
        return
    history_text = get_text(
        "flownomika_menu_1",
        throw_data={
            "side": get_text(f"side_{side}"),
            "num": data["num"],
            "l_users": view_selected_users(d_users),
        },
    )
    await state.update_data(history_text=history_text)
    await bot.edit_message_text(
        text=history_text,
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=None,
    )
    await bot.send_message(
        chat_id=query.from_user.id,
        text=get_text("enter_reason"),
        reply_markup=keyboard_markup.cancel(),
    )
    await state.set_state(Admin.enter_reason)


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "end_choise_selects",
)
async def process_end_choise_selects(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    side = data["side"]
    d_users = data["d_users"]
    if not [i for i in d_users if i["select"] != False]:
        return await query.answer(text=get_text("no_one_choice"), show_alert=True)
    history_text = get_text(
        "flownomika_menu_1",
        throw_data={
            "side": get_text(f"side_{side}"),
            "num": data["num"],
            "l_users": view_selected_users(d_users),
        },
    )
    await state.update_data(history_text=history_text)
    await bot.edit_message_text(
        text=history_text,
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=None,
    )
    await bot.send_message(
        chat_id=query.from_user.id,
        text=get_text("enter_reason"),
        reply_markup=keyboard_markup.cancel(),
    )
    await state.set_state(Admin.enter_reason)


@main_router.message(Admin.enter_reason, F.text == get_button("cancel"))
async def enter_reason_cancel(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    side = data["side"]
    await state.update_data(many_selects=True)
    await message.answer(
        get_text("canceled"), reply_markup=keyboard_markup.main_menu_admin()
    )
    await message.answer(
        text=get_text(
            "flownomika_menu_2",
            throw_data={
                "side": get_text(f"side_{side}"),
                "num": data["num"],
                "l_users": view_selected_users(data["d_users"]),
                "cpage": wrap(int(data["page"])),
                "allpage": wrap(count_page(5, len(data["d_users"]))),
            },
        ),
        reply_markup=keyboard_inline.flownomika_list_users(
            data["d_users"], is_many_selects=True, page_num=data["page"]
        ),
    )
    await state.update_data(is_many_selects=True)
    return await state.set_state(Admin.main)


@main_router.message(Admin.enter_reason)
async def enter_reason(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    text_reason = message.text.strip()
    date = extract_date(text_reason)
    text_reason = text_reason.replace(date[0], '').strip() if date else text_reason
    user = User(message.from_user.id)
    ref_admin_throw_name = f'<a href="https://t.me/@id{user.id}">{user.fio}</a>'
    mess = await bot.send_message(
        chat_id=config.CHAT_ID,
        message_thread_id=config.THREAD_ID_HISTORY,
        text=get_text(
            "history_for_admin",
            throw_data={
                "admin": ref_admin_throw_name,
                "h_data": data["history_text"],
                "reason": text_reason,
            },
        ),
    )
    date = date or get_current_date("%d.%m.%Y")
    for user in data["d_users"]:
        if not user["select"]:
            continue
        reason = Reason().create_reason
        reason.date = date[0]
        reason.id = user["id"]
        reason.reason = text_reason
        reason.owner_reason = message.from_user.id
        reason.num = data["num"]
        reason.message_id = mess.message_id
        User(user["id"]).balance_flow += int(data["num"])

    await message.answer(
        get_text("reason_recorded"),
        reply_markup=keyboard_markup.main_menu_admin(),
    )

    message_reason = MessageReason().create_message_reason(mess.message_id)
    message_reason.message_text = mess.text
    await state.set_data({})
    await state.set_state(Admin.main)
