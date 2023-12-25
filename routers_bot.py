from aiogram import Bot, Dispatcher, Router

from my_middleware import CounterMiddlewareCallbackQuery, CounterMiddlewareMessage


form_router = Router()
form_router.message.middleware(CounterMiddlewareMessage())
form_router.callback_query.middleware(CounterMiddlewareCallbackQuery())
main_router = Router()
main_router.message.middleware(CounterMiddlewareMessage())
main_router.callback_query.middleware(CounterMiddlewareCallbackQuery())