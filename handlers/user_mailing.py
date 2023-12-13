from aiogram import F
from own_utils import (
    count_page,
    delete_choose_reasons,
    get_all_reason,
    get_button,
    get_text,
    update_dict_reasons,
)
from dispatcher import main_router, bot
import keyboard_inline
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from state_classes import Admin



@main_router.message(Admin.main, F.text == get_button("mailing"))
async def user_mailing(message: Message, state: FSMContext) -> None:
    await message.answer(get_text(''))





    # while users and exception_ <= quantity_exception:
    #         try:
    #             t = get_text('extend_quantity_stocks3.2', format=False)
    #             mess = await bot.send_message(chat_id=users[-1], text=t, reply_markup=keyboard_inline.poll_extend_stocks(user.id))
    #             await bot.pin_chat_message(chat_id=users[-1], message_id=mess.message_id)
    #             users.pop()
    #             await sleep(0.3)
    #         except Exception:
    #             _ = users.pop()
    #             users.insert(0, _)
    #             set_exception.add_value(_)
    #             exception_ += 1
    #     if set_exception:
    #         for i in set_exception:
    #             q_stocks_all = get_total_quantity_stocks(int(user.id))
    #             q_stocks_ihave = get_2dd(table='users', key='briefcase', where='id_user', meaning=i, meaning_data=user.id, where_data='id_stocks', get_data='quantity_stocks')
    #             q_stocks_ihave = 0 if q_stocks_ihave is None else q_stocks_ihave
    #             weight_response = q_stocks_ihave * 100 / q_stocks_all / 2
    #             d = [i, weight_response]
    #             add_2dd(table='users', key='poll_responses', where='id_user', meaning=user.id, d=d)
    #     q_sendmess_user = q_all_user - len(users)
    #     d = [num, round(cost_stocks, 2), q_sendmess_user, q_all_user, 1]
    #     add_2dd(table='users', key='info_for_extend_stocks', where='id_user', meaning=user.id, d=d)
    #     d = {'q_sendmess_user': shell_num(q_sendmess_user),
    #         'q_all_user': shell_num(q_all_user)}
    #     await bot.send_message(call.from_user.id, get_text('extend_quantity_stocks3.3', format=True, d=d), reply_markup=keyboard_default.menu_stocks())
    #     await state.finish()