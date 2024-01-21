from aiogram import F
from own_utils import get_button, get_text
from dispatcher import main_router, bot
import keyboard_inline
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from tool_classes import User



@main_router.message(F.text == get_button("balance"))
async def balance_flow(message: Message, state: FSMContext) -> None:
    user = User(message.from_user.id)
    await message.answer(
        text=get_text("balance_info", throw_data={"flowiki": user.wrap.balance_flow}),
        reply_markup=keyboard_inline.for_what(),
    )


@main_router.callback_query(
    F.data.split(":")[0] == "action",
    F.data.split(":")[2] == "for_what",
)
async def for_what(query: CallbackQuery, state: FSMContext) -> None:
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        text=get_text("for_what"),
        message_id=query.message.message_id,
        reply_markup=None,
    )
