import emoji
from dispatcher import main_router
from own_utils import (
    get_text,
    is_human_emoji
)
from routers_bot import main_router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from state_classes import UserState
from init_db import flow_db
from aiogram.types import (
    Message,
)

from tool_classes import User


@main_router.message(Command(commands=["emoji"]))
async def set_emoji(message: Message, state: FSMContext) -> None:
    if User(message.from_user.id).emoji:
        return await message.answer(text=get_text('you_have_emoji'))
    await message.answer(text=get_text('send_emoji'))
    await state.set_state(UserState.set_emoji)

@main_router.message(UserState.set_emoji)
async def get_emoji(message: Message, state: FSMContext) -> None:
    emoji_ = emoji.emoji_list(message.text)[0]['emoji']
    if is_human_emoji(emoji_):
        return await message.answer(get_text('send_another_emoji'))
    if emoji_ in flow_db.get_all_emoji():
        return await message.answer(get_text('send_another_emoji_this_busy'))
    User(message.from_user.id).emoji = emoji_
    await message.answer(get_text('emoji_was_set'))
    await state.clear()