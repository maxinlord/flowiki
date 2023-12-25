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

from tool_classes import Reasons


@main_router.message(F.text == get_button("history_transfer"))
async def history_transfer(message: Message, state: FSMContext) -> None:
    reasons = Reasons('5255757696')
    if not list(reasons):
        return await message.answer(get_text("history_not_exists"))
    q_page = count_page(5, len(reasons))
    history_text = create_text_historys(raw_data=reasons.data, page_num=1)
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
    reasons = Reasons('5255757696')
    q_page = count_page(5, len(reasons))
    page = int(float(query.data.split(":")[-1]))
    if query.data.split(":")[1] == "to_right":
        page = page + 1 if page < q_page else 1
    else:
        page = page - 1 if page > 1 else q_page

    history_text = create_text_historys(raw_data=reasons.data, page_num=page)
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
