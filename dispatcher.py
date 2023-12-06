import logging
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
import config
from routers_bot import main_router, form_router



logging.basicConfig(level=logging.ERROR)

# prerequisites
if not config.TOKEN:
    exit("No token provided")


# init
bot = Bot(token=config.TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(form_router)
dp.include_router(main_router)