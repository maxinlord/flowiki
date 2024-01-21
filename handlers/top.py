from aiogram import F
import keyboard_markup
from own_utils import (
    get_button,
    get_text,
    wrap,
)
from dispatcher import main_router
from init_db import flow_db
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from tool_classes import Users

top_d = {1: "🥇", 2: "🥈", 3: "🥉"}


@main_router.message(F.text == get_button("top"))
async def top_flow(message: Message, state: FSMContext) -> None:
    users = Users(message.from_user.id)
    place, tops = 1, []
    for place, user in enumerate(users.to_dict_without_display, 1):
        emoji = user["emoji"]
        tops.append(
            get_text(
                "pattern_line_top",
                throw_data={
                    "fio": user["fio"],
                    "balance_flow": wrap(user["balance_flow"]),
                    "place": top_d.get(place, f"#{place}"),
                    "emoji": f'[{emoji}]' if emoji else '',
                },
            )
        )
    tops_text = "\n".join(tops)
    keyboard = ReplyKeyboardRemove()
    if users.me.rule == "user":
        keyboard = keyboard_markup.main_menu_user()
    if users.me.rule == "admin":
        keyboard = keyboard_markup.main_menu_admin()
    await message.answer(
        get_text("top_info", throw_data={"list_top": tops_text}), reply_markup=keyboard
    )
