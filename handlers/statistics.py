from dispatcher import main_router
from aiogram import F
from own_utils import (
    get_all_users_visit,
    get_button,
    get_text,
)
from routers_bot import main_router
from init_db import flow_db
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
)



@main_router.message(F.text == get_button("statistics"))
async def statistics(message: Message, state: FSMContext) -> None:
    total_num_of_flowiki = flow_db.get_total_num_of_flowiki()
    avg_num_flowiki = flow_db.get_average_num_of_flowiki()
    visits = get_all_users_visit()
    await message.answer(get_text('statistics', throw_data={
        'total_flowiki': total_num_of_flowiki,
        'avg_flowiki': avg_num_flowiki,
        'visits': visits
    }))
