from aiogram import Router

from my_middleware import LastTapMiddlewareCallbackQuery, LastTapMiddlewareMessage, BlockMainChatMiddlewareMessage

main_router = Router()
main_router.message.outer_middleware(BlockMainChatMiddlewareMessage())
main_router.message.middleware(LastTapMiddlewareMessage())
main_router.callback_query.middleware(LastTapMiddlewareCallbackQuery())


