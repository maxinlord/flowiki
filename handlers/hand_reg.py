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


@main_router.message(Admin.main, F.text == get_button("hand_reg"))
async def hand_reg(message: Message, state: FSMContext) -> None:
    id_user = message.from_user.id
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
    flow_db.update_value(key="username", where="id", meaning=id_user, value="@None")
    flow_db.update_value(
        key="fio", where="id", meaning=id_user, value=message.text.strip()
    )
    flow_db.update_value(
        key="date_reg",
        where="id",
        meaning=id_user,
        value=get_current_date("%Y-%m-%d, %H:%M:%S"),
    )
    flow_db.update_value(key="rule", where="id", meaning=id_user, value="user")
    flow_db.update_value(key="balance_flow", where="id", meaning=id_user, value=0)
    await state.set_state(Admin.main)
    await message.answer(
        get_text("user_created"), reply_markup=keyboard_markup.main_menu_admin()
    )
