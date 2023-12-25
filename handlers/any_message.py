import random
from filter_message import Block, state_is_none
from handlers.start import command_start, process_fio
from own_utils import (
    get_text,
)
from dispatcher import main_router, bot
from init_db import flow_db
import keyboard_markup
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from state_classes import Admin, Ban, FormReg, Viewer


@main_router.message(Command(commands=["update"]), Block(pass_if=False))
async def all_mes2(message: Message, state: FSMContext) -> None:
    id_user = message.from_user.id
    if not flow_db.user_exists(id_user):
        return await command_start(message, state)
    if not flow_db.rule_exists(id_user):
        await state.set_state(FormReg.fio)
        return await process_fio(message, state)
    n = random.randint(1, 8)
    rule = flow_db.get_value(key="rule", where="id", meaning=id_user)
    if rule == "admin":
        return await message.answer(
            get_text(f"hi{n}"),
            reply_markup=keyboard_markup.main_menu_admin(),
        )
    await message.answer(
        text=get_text(f"hi{n}"), reply_markup=keyboard_markup.main_menu_user()
    )


@main_router.message()
@state_is_none
async def all_mes(message: Message, state: FSMContext) -> None:
    id_user = message.from_user.id
    rule = flow_db.get_value(key="rule", where="id", meaning=id_user)
    if rule == "admin":
        await state.set_state(Admin.main)
        return await message.answer(
            get_text("again_work"),
            reply_markup=keyboard_markup.main_menu_admin(),
        )
    if rule == "ban":
        return await state.set_state(Ban.void)
    if rule == "viewer":
        return await state.set_state(Viewer.main)


@main_router.callback_query()
async def process_end_choise_selects(query: CallbackQuery, state: FSMContext) -> None:
    await bot.delete_message(
        chat_id=query.from_user.id, message_id=query.message.message_id
    )
    await query.answer(cache_time=0)
