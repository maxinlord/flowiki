import contextlib
from aiogram import F
from own_utils import (
    count_page,
    delete_choose_reasons,
    get_all_reason,
    get_button,
    get_text,
    update_dict_reasons,
)
from dispatcher import main_router, bot
import keyboard_inline
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import config
from state_classes import Admin
from tool_classes import MessageReason, User


@main_router.message(Admin.main, F.text == get_button("delete_history_reason"))
async def delete_history_reason(message: Message, state: FSMContext) -> None:
    reasons = get_all_reason()
    q_page = count_page(9, len(reasons))
    await state.update_data(reasons=reasons, page=1)
    await message.answer(
        get_text(
            "menu_delete_history_reason", throw_data={"cpage": 1, "allpage": q_page}
        ),
        reply_markup=keyboard_inline.menu_reason(reasons),
    )


@main_router.callback_query(
    F.data.split(":")[0] == "action",
    F.data.split(":")[1].in_(["history_to_del_turn_right", "history_to_del_turn_left"]),
)
async def process_turn_right(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    reasons = data["reasons"]
    q_page = count_page(9, len(reasons))
    page = int(query.data.split(":")[-1])
    if query.data.split(":")[1] == "history_to_del_turn_right":
        page = page + 1 if page < q_page else 1
    else:
        page = page - 1 if page > 1 else q_page
    await state.update_data(page=page)
    await bot.edit_message_text(
        text=get_text(
            "menu_delete_history_reason", throw_data={"cpage": page, "allpage": q_page}
        ),
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.menu_reason(page_num=page, reasons=reasons),
    )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "select_reason",
)
async def process_select_reason(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    tag_reason = query.data.split(":")[-1]
    reasons = update_dict_reasons(tag_reason, data["reasons"])
    await state.update_data(reasons=reasons)
    await bot.edit_message_reply_markup(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.menu_reason(
            page_num=data["page"], reasons=reasons
        ),
    )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "delete_reason",
)
async def del_reason(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    reasons = data["reasons"]
    choose_reasons = [reason for reason in reasons if reason["is_choose"] == True]
    if not choose_reasons:
        return await query.answer(
            text=get_text("no_one_choice_reasons"), show_alert=True
        )
    delete_choose_reasons(choose_reasons)
    await bot.edit_message_text(
        text=get_text("reasons_deleted"),
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=None,
    )
    for reason in choose_reasons:
        message_reason = MessageReason(reason['message_id'])
        text: str = message_reason.message_text
        fio = User(reason['id']).fio
        fio_to_replace = get_text('fio_to_replace', throw_data={'fio': fio})
        fio_list = fio.split()
        [text:=text.replace(i, 'name') for i in fio_list]
        text = text.replace('name name', fio_to_replace)
        message_reason.message_text = text
        with contextlib.suppress(Exception):
            await bot.edit_message_text(chat_id=config.CHAT_ID, message_id=message_reason.message_id, text=message_reason.message_text)
    
