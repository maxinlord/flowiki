from dispatcher import main_router, form_router
from aiogram import F
from filter_message import Block, state_is_none
from own_utils import (
    get_all_users_visit,
    get_button,
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
from aiogram.filters import CommandStart, CommandObject, Command
from state_classes import Admin, Ban, FormReg, Viewer
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
)
from aiogram.utils.deep_linking import create_start_link

from tool_classes import User


@main_router.message(F.text == get_button("statistics"))
async def statistics(message: Message, state: FSMContext) -> None:
    total_num_of_flowiki = flow_db.get_total_num_of_flowiki()
    avg_num_flowiki = flow_db.get_average_num_of_flowiki()
    visits = get_all_users_visit()
    await message.answer(get_text('statistics', throw_data={
        'total_flowiki': total_num_of_flowiki,
        'avg_flowiki': avg_num_flowiki,
        'visits': visits
    }))
