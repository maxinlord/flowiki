from aiogram import F
from dispatcher import main_router
from aiogram.types import Message

from state_classes import Admin

@main_router.message(Admin.main, F.photo)
async def handle_photo(message: Message):
    await message.answer(message.photo[-1].file_id)



