from aiogram import F
from own_utils import (
    count_page,
    get_admin_preset,
    get_all_reason,
    get_button,
    get_current_date,
    get_dict_users_with_filter,
    get_text,
    update_dict_users,
    view_selected_users,
    wrap,
)
from dispatcher import main_router, bot
from init_db import flow_db
import keyboard_inline, keyboard_markup
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import config

from state_classes import Admin


@main_router.message(Admin.main, F.text == get_button("delete_history_reason"))
async def delete_history_reason(message: Message, state: FSMContext) -> None:
    reasons = get_all_reason()
    await message.answer(get_text('delete_history_reason'),
                         reply_markup=keyboard_inline.menu_reason(reasons))