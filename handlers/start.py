from dispatcher import main_router, form_router
from aiogram import F
from filter_message import Block, state_is_none
from own_utils import (
    get_current_date,
    get_text,
)
from dispatcher import bot
from routers_bot import main_router, form_router
from init_db import flow_db
import keyboard_inline, keyboard_markup
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import config
from aiogram.filters import CommandStart, CommandObject
from state_classes import Admin, Ban, FormReg, Viewer
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
)

from tool_classes import Item, User

# result: 'https://t.me/MyBot?start=Zm9v'


@main_router.message(Block())
async def chat_block(message: Message, state: FSMContext) -> None:
    return


@form_router.message(CommandStart(), Block(pass_if=False))
async def command_start(
    message: Message, state: FSMContext, command: CommandObject
) -> None:
    if not flow_db.user_exists(message.from_user.id):
        await state.set_state(FormReg.fio)
        return await message.answer(
            get_text("hi_reg"),
            reply_markup=ReplyKeyboardRemove(),
        )
    user = User(message.from_user.id)
    arg = command.args
    if arg and flow_db.item_exists(arg):
        item = Item(arg)
        keyboard = (
            keyboard_inline.buy_item_user(who=user.id, id_item=arg)
            if user.rule == "user"
            else keyboard_inline.buy_item_admin(id_item=arg)
        )
        if item.photo == "-":
            return await message.answer(
                text=get_text(
                    "item_display_for_purchase",
                    throw_data={
                        "name": item.name,
                        "description": item.description,
                        "price": item.price_str,
                    },
                ),
                reply_markup=keyboard,
            )
        return await message.answer_photo(
            photo=item.photo,
            caption=get_text(
                "item_display_for_purchase",
                throw_data={
                    "name": item.name,
                    "description": item.description,
                    "price": item.price_str,
                },
            ),
            reply_markup=keyboard,
        )

    if user.rule == "user":
        return await message.answer(
            get_text("hi5"),
            reply_markup=keyboard_markup.main_menu_user(),
        )
    if user.rule == "admin":
        await state.set_state(Admin.main)
        return await message.answer(
            get_text("hi5"),
            reply_markup=keyboard_markup.main_menu_admin(),
        )
    if user.rule == "ban":
        return await state.set_state(Ban.void)
    if user.rule == "viewer":
        return await state.set_state(Viewer.main)


@form_router.message(FormReg.fio)
async def process_fio(message: Message, state: FSMContext) -> None:
    id_user = message.from_user.id
    photo = await message.from_user.get_profile_photos()
    try:
        photo_id = photo.photos[0][0].file_id
    except Exception:
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
    user = User(query.from_user.id)
    data = await state.get_data()
    user = user[user.id]
    user.username = f"@{query.from_user.username}"
    user.fio = data["fio"].strip()
    user.date_reg = get_current_date("%Y-%m-%d, %H:%M:%S")
    user.rule = "admin"
    user.balance_flow = 0
    await state.set_state(Admin.main)
    await bot.edit_message_text(
        chat_id=user.id,
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
    user = User(query.from_user.id)
    data = await state.get_data()
    user = user[user.id]
    user.username = f"@{query.from_user.username}"
    user.fio = data["fio"].strip()
    user.date_reg = get_current_date("%Y-%m-%d, %H:%M:%S")
    user.rule = "user"
    user.balance_flow = 0
    await state.clear()
    await bot.edit_message_text(
        chat_id=user.id,
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
    user = User(query.from_user.id)
    data = await state.get_data()
    user = user[user.id]
    user.username = f"@{query.from_user.username}"
    user.fio = data["fio"].strip()
    user.date_reg = get_current_date("%Y-%m-%d, %H:%M:%S")
    user.rule = "viewer"
    user.balance_flow = 0
    await state.set_state(Viewer.main)
    await bot.edit_message_text(
        chat_id=user.id,
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
    user = User(query.data.split(":")[2])
    data = await state.get_data()
    user = user[user.id]
    user.username = f"@{query.from_user.username}"
    user.date_reg = get_current_date("%Y-%m-%d, %H:%M:%S")
    user.rule = "ban"
    user.balance_flow = 0
    await bot.send_message(
        chat_id=user.id,
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


@form_router.callback_query(
    F.data.split(":")[0] == "action", F.data.split(":")[1] == "buy_item_user"
)
async def buy_item(query: CallbackQuery, state: FSMContext) -> None:
    user = User(query.data.split(":")[2])
    item = Item(query.data.split(":")[3])
    if (item.quantity - 1) < 0:
        return await query.answer(get_text("not_enough_items"), show_alert=True)
    if (user.balance_flow - item.price) < 0:
        return await query.answer(get_text("not_enough_flowik"), show_alert=True)
    user.balance_flow -= item.price
    item.quantity -= 1
    await query.message.delete()
    text_purchase = get_text("item_purchased", throw_data={"item_name": item.name})
    await query.message.answer(text=text_purchase)
    await bot.send_message(
        chat_id=config.CHAT_ID,
        message_thread_id=config.THREAD_ID_HISTORY,
        text=text_purchase,
    )


@form_router.callback_query(
    F.data.split(":")[0] == "action", F.data.split(":")[1] == "buy_item_admin"
)
async def buy_item(query: CallbackQuery, state: FSMContext) -> None:
    pass
