from aiogram import F
from own_utils import (
    get_button,
    get_text,
)
from dispatcher import main_router
import keyboard_markup
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from state_classes import Admin


@main_router.message(Admin.main, F.text == get_button("options_for_admin"))
async def options_for_admin(message: Message, state: FSMContext) -> None:
    await message.answer(text=get_text('menu_options'), reply_markup=keyboard_markup.menu_options())

@main_router.message(Admin.main, F.text == get_button("back"))
async def options_cancel(message: Message, state: FSMContext) -> None:
    await message.answer(text=get_text('main_menu'), reply_markup=keyboard_markup.main_menu_admin())