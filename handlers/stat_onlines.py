from dispatcher import main_router
from own_utils import (
    get_text,
)
from routers_bot import main_router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandObject, Command
from aiogram.types import (
    Message,
)

from tool_classes import User

# stat_command = get_text('stat_online')

@main_router.message(Command(commands=['online']))    
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

