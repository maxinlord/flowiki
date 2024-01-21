from aiogram.filters import Filter, CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import config


def state_is_none(func):
    async def wrapper(message: Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state is not None:
            return
        await func(message, state)

    return wrapper
