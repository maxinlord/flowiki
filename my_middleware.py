from pprint import pprint
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from own_utils import get_current_date
from state_classes import Admin, Viewer
from tool_classes import User
import config

class LastTapMiddlewareMessage(BaseMiddleware):
    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        state: FSMContext
    ) -> Any:
        date = get_current_date('%d.%m.%Y, %H:%M:%S')
        user = User(event.from_user.id)
        user.last_tap_date = date
        user.last_tap_button = event.text
        return await handler(event, state)

class LastTapMiddlewareCallbackQuery(BaseMiddleware):
    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        state: FSMContext
    ) -> Any:
        date = get_current_date('%d.%m.%Y, %H:%M:%S')
        user = User(event.from_user.id)
        user.last_tap_date = date
        user.last_tap_button = event.data
        return await handler(event, state)


class BlockMainChatMiddlewareMessage(BaseMiddleware):
    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        state: FSMContext
    ) -> Any:
        if str(event.chat.id) == config.CHAT_ID:
            return
        return await handler(event, state)