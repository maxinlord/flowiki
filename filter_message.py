from aiogram.filters import Filter, CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import config

class Block(Filter):
    def __init__(self, ids: list = None, pass_if: bool = True) -> None:
        if ids is None:
            ids = []
        self.pass_if = pass_if
        if ids:
            ids = ids.append(config.CHAT_ID)
            self.ids = ids
            return
        self.ids = [config.CHAT_ID]

    async def __call__(self, message: Message) -> bool:
        if self.pass_if:
            return str(message.chat.id) in self.ids
        return str(message.chat.id) not in self.ids


def state_is_none(func):
    async def wrapper(message: Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state is not None:
            return
        await func(message, state)

    return wrapper
