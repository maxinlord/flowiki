from aiogram import F
from own_utils import (
    create_custom_id,
    get_button,
    get_current_date,
    get_text,
)
from dispatcher import main_router
from init_db import flow_db
import keyboard_markup
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from state_classes import Admin, FormReg
from tool_classes import User


@main_router.message(Admin.main, F.text == get_button("hand_reg"))
async def hand_reg(message: Message, state: FSMContext) -> None:
    await state.set_state(FormReg.hand_reg)
    await message.answer(
        get_text("enter_fio_user"),
        reply_markup=keyboard_markup.cancel(),
    )


@main_router.message(FormReg.hand_reg, F.text == get_button("cancel"))
async def process_create_user_cancel(message: Message, state: FSMContext) -> None:
    await state.set_state(Admin.main)
    await message.answer(
        get_text("user_create_cancel"), reply_markup=keyboard_markup.main_menu_admin()
    )


@main_router.message(FormReg.hand_reg)
async def process_create_user(message: Message, state: FSMContext) -> None:
    id_user = create_custom_id()
    flow_db.add_user(id_user)
    user = User(id_user)
    user.username = '@None'
    user.fio = message.text.strip()
    user.date_reg = get_current_date("%Y-%m-%d, %H:%M:%S")
    user.rule = 'user'
    user.balance_flow = 0
    await state.set_state(Admin.main)
    await message.answer(
        get_text("user_created"), reply_markup=keyboard_markup.main_menu_admin()
    )
