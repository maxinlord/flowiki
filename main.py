import asyncio
import html
import logging
import os
from pprint import pprint
import sys
from typing import Any, Dict
from aiogram import F, Router, html
from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
)
from aiogram.types import FSInputFile
from aiogram.filters import Filter

from db_func import flow_db
import config
from own_utils import *
import keyboard_inline
import keyboard_markup

TOKEN = config.TOKEN
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)

form_router = Router()
main_router = Router()


class FormReg(StatesGroup):
    fio = State()
    pending_review = State()
    hand_reg = State()


class Admin(StatesGroup):
    main = State()
    enter_reason = State()
    enter_another_quantity = State()


class Viewer(StatesGroup):
    main = State()


class Ban(StatesGroup):
    void = State()


class Block(Filter):
    def __init__(self, ids: list = [], pass_if: bool = True) -> None:
        self.pass_if = pass_if
        if ids:
            ids = ids.append(config.CHAT_ID)
            self.ids = ids
            return
        self.ids = [config.CHAT_ID]

    async def __call__(self, message: Message) -> bool:
        if self.pass_if:
            return str(message.chat.id) in self.ids
        return str(message.chat.id) not in self.ids


def state_is_none(func):
    async def wrapper(message: Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state is not None:
            return
        await func(message, state)

    return wrapper


@main_router.message(Block())
async def chat_block(message: Message, state: FSMContext) -> None:
    return


@form_router.message(CommandStart(), Block(pass_if=False))
@state_is_none
async def command_start(message: Message, state: FSMContext) -> None:
    id_user = message.from_user.id
    if flow_db.user_exists(id_user):
        pprint(message)
        return await message.answer(
            get_text("hi"),
            reply_markup=keyboard_markup.main_menu_user(),
        )
    await state.set_state(FormReg.fio)
    await message.answer(
        get_text("hi_reg"),
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(FormReg.fio)
async def process_fio(message: Message, state: FSMContext) -> None:
    id_user = message.from_user.id
    photo = await message.from_user.get_profile_photos()
    try:
        photo_id = photo.photos[0][0].file_id
    except:
        photo_id = flow_db.get_value(
            key="box",
            where="name",
            meaning="photo_id_for_no_exists_photo",
            table="values",
        )
    finally:
        await bot.send_photo(
            chat_id=config.CHAT_ID,
            message_thread_id=config.THREAD_ID_PENDING_REVIEW,
            photo=photo_id,
            caption=get_text("request", throw_data={"fio": message.text}),
            reply_markup=keyboard_inline.keyboard_for_rule(id_user),
        )
    await state.update_data(fio=message.text)
    await state.set_state(FormReg.pending_review)
    await message.answer(get_text("pending_wait"))


@form_router.callback_query(
    FormReg.pending_review, F.data.split(":") == ["action", "confirm_reg", "admin"]
)
async def process_confirm_reg_admin(query: CallbackQuery, state: FSMContext) -> None:
    id_user = query.from_user.id
    data = await state.get_data()
    flow_db.add_user(id_user)
    flow_db.update_value(
        key="username",
        where="id",
        meaning=id_user,
        value=f"@{query.from_user.username}",
    )
    flow_db.update_value(
        key="fio", where="id", meaning=id_user, value=data["fio"].strip()
    )
    flow_db.update_value(
        key="date_reg",
        where="id",
        meaning=id_user,
        value=get_current_date("%Y-%m-%d, %H:%M:%S"),
    )
    flow_db.update_value(key="rule", where="id", meaning=id_user, value="admin")
    flow_db.update_value(key="balance_flow", where="id", meaning=id_user, value=0)
    await state.set_state(Admin.main)
    await bot.edit_message_text(
        chat_id=id_user,
        message_id=query.message.message_id,
        text=get_text("registered"),
    )
    await bot.send_message(
        chat_id=query.from_user.id,
        text=get_text("congratulation_reg_admin"),
        reply_markup=keyboard_markup.main_menu_admin(),
    )


@form_router.callback_query(
    FormReg.pending_review, F.data.split(":") == ["action", "confirm_reg", "user"]
)
async def process_confirm_reg_user(query: CallbackQuery, state: FSMContext) -> None:
    id_user = query.from_user.id
    data = await state.get_data()
    flow_db.add_user(id_user)
    flow_db.update_value(
        key="username",
        where="id",
        meaning=id_user,
        value=f"@{query.from_user.username}",
    )
    flow_db.update_value(
        key="fio", where="id", meaning=id_user, value=data["fio"].strip()
    )
    flow_db.update_value(
        key="date_reg",
        where="id",
        meaning=id_user,
        value=get_current_date("%Y-%m-%d, %H:%M:%S"),
    )
    flow_db.update_value(key="rule", where="id", meaning=id_user, value="user")
    flow_db.update_value(key="balance_flow", where="id", meaning=id_user, value=0)
    await state.clear()
    await bot.edit_message_text(
        chat_id=id_user,
        message_id=query.message.message_id,
        text=get_text("registered"),
    )
    await bot.send_message(
        chat_id=query.from_user.id,
        text=get_text("congratulation_reg_user"),
        reply_markup=keyboard_markup.main_menu_user(),
    )


@form_router.callback_query(
    FormReg.pending_review, F.data.split(":") == ["action", "confirm_reg", "viewer"]
)
async def process_confirm_reg_user(query: CallbackQuery, state: FSMContext) -> None:
    id_user = query.from_user.id
    data = await state.get_data()
    flow_db.add_user(id_user)
    flow_db.update_value(
        key="username",
        where="id",
        meaning=id_user,
        value=f"@{query.from_user.username}",
    )
    flow_db.update_value(
        key="fio", where="id", meaning=id_user, value=data["fio"].strip()
    )
    flow_db.update_value(
        key="date_reg",
        where="id",
        meaning=id_user,
        value=get_current_date("%Y-%m-%d, %H:%M:%S"),
    )
    flow_db.update_value(key="rule", where="id", meaning=id_user, value="viewer")
    flow_db.update_value(key="balance_flow", where="id", meaning=id_user, value=0)
    await state.set_state(Viewer.main)
    await bot.edit_message_text(
        chat_id=id_user,
        message_id=query.message.message_id,
        text=get_text("registered"),
    )
    await bot.send_message(
        chat_id=query.from_user.id,
        text=get_text("congratulation_reg_viewer"),
        reply_markup=None,
    )


@form_router.callback_query(
    F.data.split(":")[0] == "rule", F.data.split(":")[1] == "admin"
)
async def process_answer_on_request_admin(
    query: CallbackQuery, state: FSMContext
) -> None:
    await bot.send_message(
        chat_id=query.data.split(":")[2],
        text=get_text("you_admin"),
        reply_markup=keyboard_inline.confirm_reg_admin(),
    )
    old_caption = query.message.caption
    await bot.edit_message_caption(
        chat_id=config.CHAT_ID,
        message_id=query.message.message_id,
        caption=get_text("answer_on_request_admin", throw_data={"text": old_caption}),
        reply_markup=None,
    )


@form_router.callback_query(
    F.data.split(":")[0] == "rule", F.data.split(":")[1] == "user"
)
async def process_answer_on_request_user(
    query: CallbackQuery, state: FSMContext
) -> None:
    await bot.send_message(
        chat_id=query.data.split(":")[2],
        text=get_text("you_user"),
        reply_markup=keyboard_inline.confirm_reg_user(),
    )
    old_caption = query.message.caption
    await bot.edit_message_caption(
        chat_id=config.CHAT_ID,
        message_id=query.message.message_id,
        caption=get_text("answer_on_request_user", throw_data={"text": old_caption}),
        reply_markup=None,
    )


@form_router.callback_query(
    F.data.split(":")[0] == "rule", F.data.split(":")[1] == "viewer"
)
async def process_answer_on_request_user(
    query: CallbackQuery, state: FSMContext
) -> None:
    await bot.send_message(
        chat_id=query.data.split(":")[2],
        text=get_text("you_viewer"),
        reply_markup=keyboard_inline.confirm_reg_viewer(),
    )
    old_caption = query.message.caption
    await bot.edit_message_caption(
        chat_id=config.CHAT_ID,
        message_id=query.message.message_id,
        caption=get_text("answer_on_request_viewer", throw_data={"text": old_caption}),
        reply_markup=None,
    )


@form_router.callback_query(
    F.data.split(":")[0] == "rule", F.data.split(":")[1] == "ban"
)
async def process_answer_on_request_ban(
    query: CallbackQuery, state: FSMContext
) -> None:
    id_user_to_ban = query.data.split(":")[2]
    flow_db.add_user(id_user_to_ban)
    flow_db.update_value(
        key="username",
        where="id",
        meaning=id_user_to_ban,
        value=f"@{query.from_user.username}",
    )
    flow_db.update_value(key="rule", where="id", meaning=id_user_to_ban, value="ban")
    await bot.send_message(
        chat_id=id_user_to_ban,
        text=get_text("ban"),
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(Ban.void)
    old_caption = query.message.caption
    await bot.edit_message_caption(
        chat_id=config.CHAT_ID,
        message_id=query.message.message_id,
        caption=get_text("answer_on_request", throw_data={"text": old_caption}),
        reply_markup=None,
    )


@form_router.callback_query(
    F.data.split(":")[0] == "action", F.data.split(":")[1] == "repeat_fio"
)
async def process_repeat_fio(query: CallbackQuery, state: FSMContext) -> None:
    await bot.delete_message(
        chat_id=config.CHAT_ID, message_id=query.message.message_id
    )
    await bot.send_message(
        chat_id=query.data.split(":")[2],
        text=get_text("repeat_fio"),
        reply_markup=keyboard_inline.confirm_repeat_fio(),
    )


@form_router.callback_query(
    FormReg.pending_review,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "enter_repeat_fio",
)
async def process_enter_repeat_fio(query: CallbackQuery, state: FSMContext) -> None:
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        text=get_text("enter_repeat_fio"),
        message_id=query.message.message_id,
    )
    await state.set_state(FormReg.fio)


@main_router.message(F.text == get_button("balance"))
@state_is_none
async def balance_flow(message: Message, state: FSMContext) -> None:
    quantity_flow = flow_db.get_value(
        key="balance_flow", where="id", meaning=message.from_user.id
    )
    await message.answer(
        text=get_text("balance_info", throw_data={"flowiki": wrap(quantity_flow)}),
        reply_markup=keyboard_inline.for_what(),
    )


@form_router.callback_query(
    F.data.split(":")[0] == "action",
    F.data.split(":")[2] == "for_what",
)
async def for_what(query: CallbackQuery, state: FSMContext) -> None:
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        text=get_text("for_what"),
        message_id=query.message.message_id,
        reply_markup=None,
    )


@main_router.message(F.text == get_button("top"))
async def top_flow(message: Message, state: FSMContext) -> None:
    raw_data = flow_db.get_all_line_key(
        key="fio, balance_flow, rule", order="balance_flow"
    )
    place, tops = 1, []
    for i in raw_data:
        if i["rule"] == "admin":
            continue
        tops.append(
            get_text(
                "pattern_line_top",
                throw_data={
                    "fio": i["fio"],
                    "balance": wrap(i["balance_flow"]),
                    "place": place,
                },
            )
        )
        place += 1
    tops_text = "\n".join(tops)
    await message.answer(get_text("top_info", throw_data={"list_top": tops_text}))


@main_router.message(Admin.main, F.text == get_button("hand_reg"))
async def hand_reg(message: Message, state: FSMContext) -> None:
    id_user = message.from_user.id
    await state.set_state(FormReg.hand_reg)
    await message.answer(
        get_text("enter_fio_user"),
        reply_markup=keyboard_markup.cancel(),
    )


@main_router.message(FormReg.hand_reg, F.text == get_button("cancel"))
async def process_create_user_cancel(message: Message, state: FSMContext) -> None:
    await state.set_state(Admin.main)
    await message.answer(
        get_text("user_create_cancel"), reply_markup=keyboard_markup.main_menu_admin()
    )


@main_router.message(FormReg.hand_reg)
async def process_create_user(message: Message, state: FSMContext) -> None:
    id_user = create_custom_id()
    flow_db.add_user(id_user)
    flow_db.update_value(key="username", where="id", meaning=id_user, value=f"@None")
    flow_db.update_value(
        key="fio", where="id", meaning=id_user, value=message.text.strip()
    )
    flow_db.update_value(
        key="date_reg",
        where="id",
        meaning=id_user,
        value=get_current_date("%Y-%m-%d, %H:%M:%S"),
    )
    flow_db.update_value(key="rule", where="id", meaning=id_user, value="user")
    flow_db.update_value(key="balance_flow", where="id", meaning=id_user, value=0)
    await state.set_state(Admin.main)
    await message.answer(
        get_text("user_created"), reply_markup=keyboard_markup.main_menu_admin()
    )


@main_router.message(F.text == get_button("history_transfer"))
async def history_transfer(message: Message, state: FSMContext) -> None:
    raw_data = flow_db.get_all_line_key(
        key="id, reason, owner_reason, date, num",
        order="date",
        table="history_reasons",
    )
    raw_data = filter_(raw_data, id=str(message.from_user.id))
    if not raw_data:
        return await message.answer(get_text("history_not_exists"))
    q_page = count_page(5, len(raw_data))
    history_text = create_text_historys(raw_data=raw_data, page_num=1)
    await message.answer(
        get_text(
            "history_info",
            throw_data={
                "list_historys": history_text,
                "allpage": wrap(q_page),
                "cpage": wrap(1),
            },
        ),
        reply_markup=keyboard_inline.arrows(page_num=1),
    )


@main_router.callback_query(
    F.data.split(":")[0] == "action",
    F.data.split(":")[1].in_(["to_right", "to_left"]),
)
async def process_turn_right(query: CallbackQuery, state: FSMContext) -> None:
    raw_data = flow_db.get_all_line_key(
        key="id, reason, owner_reason, date, num",
        order="date",
        table="history_reasons",
    )
    raw_data = filter_(raw_data, id=str(query.from_user.id))
    q_page = count_page(5, len(raw_data))
    page = int(query.data.split(":")[-1])
    if query.data.split(":")[1] == "turn_right":
        page = page + 1 if page < q_page else 1
    else:
        page = page - 1 if page > 1 else q_page

    history_text = create_text_historys(raw_data=raw_data, page_num=page)
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        text=get_text(
            "history_info",
            throw_data={
                "list_historys": history_text,
                "allpage": wrap(q_page),
                "cpage": wrap(page),
            },
        ),
        reply_markup=keyboard_inline.arrows(page_num=page),
    )


@main_router.message(Admin.main, F.text == get_button("flownomika"))
async def flownomika(message: Message, state: FSMContext) -> None:
    await state.update_data(
        side="+", num=None, is_many_selects=False, d_users=None, page=1
    )
    await message.answer(
        get_text(
            "flownomika_menu_1",
            throw_data={
                "side": "Начисление",
                "num": "Не указано",
                "l_users": "Не указано",
            },
        ),
        reply_markup=keyboard_inline.flownomika_menu(),
    )


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
                "side": "Начисление" if side == "+" else "Штраф",
                "num": "Не указано",
                "l_users": "Не указано",
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
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        text=get_text("enter_another_quantity"),
        reply_markup=None,
    )
    await state.set_state(Admin.enter_another_quantity)


@main_router.message(Admin.enter_another_quantity)
async def enter_another_quantity(message: Message, state: FSMContext) -> None:
    if not message.text.isnumeric():
        return
    data = await state.get_data()
    side = data["side"]
    d_users = get_data_users()
    await state.update_data(num=f"{side}{message.text}", d_users=d_users)
    await message.answer(
        get_text(
            "flownomika_menu_2",
            throw_data={
                "side": "Начисление" if side == "+" else "Штраф",
                "num": f"{side}{message.text}",
                "l_users": "Не указано",
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
    d_users = get_data_users()
    await state.update_data(num=num, d_users=d_users)
    await bot.edit_message_text(
        text=get_text(
            "flownomika_menu_2",
            throw_data={
                "side": "Начисление" if data["side"] == "+" else "Штраф",
                "num": num,
                "l_users": "Не указано",
                "cpage": wrap(1),
                "allpage": wrap(count_page(5, len(d_users))),
            },
        ),
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.flownomika_list_users(d_users),
    )


@main_router.callback_query(
    Admin.main, F.data.split(":")[0] == "action", F.data.split(":")[1] == "turn_left"
)
async def process_turn_left(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    q_page = count_page(5, len(data["d_users"]))
    if q_page == 1:
        return
    page = int(query.data.split(":")[-1].split('.')[0])
    page = page - 1 if page > 1 else q_page
    await state.update_data(page=page)
    await bot.edit_message_text(
        text=get_text(
            "flownomika_menu_2",
            throw_data={
                "side": "Начисление" if data["side"] == "+" else "Штраф",
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
    Admin.main, F.data.split(":")[0] == "action", F.data.split(":")[1] == "turn_right"
)
async def process_turn_right(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    q_page = count_page(5, len(data["d_users"]))
    if q_page == 1:
        return
    page = int(query.data.split(":")[-1].split('.')[0])
    page = page + 1 if page < q_page else 1
    await state.update_data(page=page)
    await bot.edit_message_text(
        text=get_text(
            "flownomika_menu_2",
            throw_data={
                "side": "Начисление" if data["side"] == "+" else "Штраф",
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
                    "side": "Начисление" if data["side"] == "+" else "Штраф",
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
            "side": "Начисление" if data["side"] == "+" else "Штраф",
            "num": data["num"],
            "l_users": view_selected_users(d_users),
            "cpage": wrap(int(data["page"])),
            "allpage": wrap(count_page(5, len(d_users))),
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
    if not [i for i in data["d_users"] if i["select"] != False]:
        return await query.answer(text=get_text("no_one_choice"), show_alert=True)
    history_text = get_text(
        "flownomika_menu_1",
        throw_data={
            "side": "Начисление" if data["side"] == "+" else "Штраф",
            "num": data["num"],
            "l_users": view_selected_users(data["d_users"]),
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
    await state.update_data(many_selects=True)
    await message.answer(
        get_text("canceled"), reply_markup=keyboard_markup.main_menu_admin()
    )
    await message.answer(
        text=get_text(
            "flownomika_menu_2",
            throw_data={
                "side": "Начисление" if data["side"] == "+" else "Штраф",
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
    for user in data["d_users"]:
        if not user["select"]:
            continue
        date = get_current_date("%Y-%m-%d, %H:%M:%S")
        flow_db.add_new_reason(
            user["id"], message.text, message.from_user.id, date, data["num"]
        )
        flow_db.add_value(
            key="balance_flow", where="id", meaning=user["id"], value=int(data["num"])
        )
    names = [user["name"] for user in data["d_users"] if user["select"]]
    await message.answer(
        get_text(
            "reason_recorded",
            throw_data={"name": ",".join(names).strip(","), "num": data["num"]},
        ),
        reply_markup=keyboard_markup.main_menu_admin(),
    )
    id_user = message.from_user.id
    name_admin = flow_db.get_value(key="fio", where="id", meaning=str(id_user))
    name_admin = f'<a href="https://t.me/@id{id_user}">{name_admin}</a>'
    reason = message.text.strip()
    await bot.send_message(
        chat_id=config.CHAT_ID,
        message_thread_id=config.THREAD_ID_HISTORY,
        text=get_text(
            "history_for_admin",
            throw_data={
                "admin": name_admin,
                "h_data": data["history_text"],
                "reason": reason,
            },
        ),
    )
    await state.set_data({})
    await state.set_state(Admin.main)


@main_router.message(Admin.main, F.text == "file")
async def get_file(message: Message):
    await message.answer(get_text("files"), reply_markup=keyboard_inline.get_files_k())
    # get_xlsx_table(flow_db.conn, 'users')
    # await message.answer_document(document=open('users.xlsx', 'rb'))


@main_router.callback_query(Admin.main, F.data.split(":")[0] == "name_table")
async def answer_button(call: CallbackQuery, state: FSMContext):
    name_table = call.data.split(":")[1]
    get_xlsx_table(flow_db.conn, f"{name_table}")
    # with open(f'{name_table}.xlsx', 'rb') as file:
    await bot.send_document(
        chat_id=call.from_user.id, document=FSInputFile(f"{name_table}.xlsx")
    )


@main_router.message(Admin.main, F.photo)
async def handle_photo(message: Message):
    await message.answer(message.photo[-1].file_id)


@main_router.message(Admin.main, F.document)
async def handle_docs(message: Message):
    file_name = message.document.file_name
    if is_xlsx_extend(file_name):
        flow_db.close(flow_db.conn)
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        try:
            os.remove(f"{file_name}")
        except:
            pass
        await bot.download_file(file.file_path, f"{file_name}")
        conn, cur = flow_db.create_new_connection()
        write_excel_to_db(excel_file=file_name, conn=conn)
        flow_db.conn, flow_db.cur = conn, cur
        return await message.answer(get_text("handle_docs.done"))
    await message.answer(get_text("handle_docs.error"))


# @main_router.message(Command("update"))
# async def update(message: Message, state: FSMContext) -> None:
#     await all_mes(message, state)


@main_router.message(Command(commands=["update"]), Block(pass_if=False))
async def all_mes2(message: Message, state: FSMContext) -> None:
    id_user = message.from_user.id
    if not flow_db.user_exists(id_user):
        return await command_start(message, state)
    if not flow_db.rule_exists(id_user):
        await state.set_state(FormReg.fio)
        return await process_fio(message, state)
    n = random.randint(1, 8)
    rule = flow_db.get_value(key="rule", where="id", meaning=id_user)
    if rule == "admin":
        return await message.answer(
            get_text(f"hi{n}"),
            reply_markup=keyboard_markup.main_menu_admin(),
        )
    await message.answer(
        text=get_text(f"hi{n}"), reply_markup=keyboard_markup.main_menu_user()
    )


@main_router.message()
@state_is_none
async def all_mes(message: Message, state: FSMContext) -> None:
    id_user = message.from_user.id
    rule = flow_db.get_value(key="rule", where="id", meaning=id_user)
    if rule == "admin":
        await state.set_state(Admin.main)
        return await message.answer(
            get_text("again_work"),
            reply_markup=keyboard_markup.main_menu_admin(),
        )
    if rule == "ban":
        return await state.set_state(Ban.void)
    if rule == "viewer":
        return await state.set_state(Viewer.main)


async def main() -> None:
    dp = dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(form_router)
    dp.include_router(main_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
