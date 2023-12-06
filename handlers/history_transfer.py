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


@main_router.message(F.text == get_button("history_transfer"))
async def history_transfer(message: Message, state: FSMContext) -> None:
    raw_data = flow_db.get_all_line_key(
        key="id, reason, owner_reason, date, num",
        order="date",
        table="history_reasons",
    )
    raw_data = [history for history in raw_data if history['id'] == str(message.from_user.id)]
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
    raw_data = [history for history in raw_data if history['id'] == str(query.from_user.id)]
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
