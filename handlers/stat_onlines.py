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
from aiogram.filters import CommandStart, CommandObject, Command
from state_classes import Admin, Ban, FormReg, Viewer
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
)
from aiogram.utils.deep_linking import create_start_link

from tool_classes import User

# stat_command = get_text('stat_online')

@form_router.message(Command(commands=['stat']))
async def command_stat_online(
    message: Message, state: FSMContext, command: CommandObject
) -> None:
    stats = ""
    for id_user in User('pass'):
        user = User(id_user)
        if not user.last_tap_date:
            continue
        line = get_text(
            "pattern_line_for_stat_online",
            throw_data={"name": user.fio, "date_online": user.last_tap_date, "button": user.last_tap_button},
        )
        stats += f'{line}\n'

    await message.answer(text=get_text("stat_online", throw_data={'stat': stats}))
