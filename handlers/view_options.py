from aiogram import F
from own_utils import (
    count_page,
    create_text_historys,
    get_button,
    get_text,
    wrap,
)
from dispatcher import main_router, bot
from init_db import flow_db
import keyboard_inline
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from state_classes import Admin


@main_router.message(Admin.main, F.text == get_button("display"))
async def display(message: Message, state: FSMContext) -> None:
    display = flow_db.get_value(
        table="users", key="display", where="id", meaning=message.from_user.id
    )
    await message.answer(
        text=get_text("menu_display"),
        reply_markup=keyboard_inline.set_display(select=display),
    )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "set",
    F.data.split(":")[2].in_(["display_sername_name", "display_name_sername"]),
)
async def set_display(query: CallbackQuery, state: FSMContext) -> None:
    display = query.data.split(":")[2]
    await query.answer(cache_time=1)
    flow_db.update_value(
        table="users",
        key="display",
        where="id",
        meaning=query.from_user.id,
        value=display,
    )
    try:
        await bot.edit_message_reply_markup(
            chat_id=query.from_user.id,
            message_id=query.message.message_id,
            reply_markup=keyboard_inline.set_display(display),
        ),
    except:
        pass
