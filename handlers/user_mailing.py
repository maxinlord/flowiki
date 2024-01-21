from asyncio import sleep
from aiogram import F
from own_utils import (
    count_page,
    delete_choose_reasons,
    get_all_reason,
    get_button,
    get_text,
    update_dict_reasons,
    update_dict_users,
)
from dispatcher import main_router, bot
import keyboard_inline, keyboard_markup
from aiogram.types import Message, CallbackQuery
from aiogram.utils.callback_answer import CallbackAnswer
from aiogram.fsm.context import FSMContext

from state_classes import Admin
from tool_classes import Users


@main_router.message(Admin.main, F.text == get_button("mailing"))
async def user_mailing(message: Message, state: FSMContext) -> None:
    await message.answer(
        get_text("send_message_for_mail"), reply_markup=keyboard_markup.cancel()
    )
    await state.set_state(Admin.send_message_for_mail)


@main_router.message(Admin.send_message_for_mail)
async def get_mess_mail(message: Message, state: FSMContext) -> None:
    if message.text == get_button("cancel"):
        await state.set_state(Admin.main)
        return await message.answer(
            text=get_text("canceled"), reply_markup=keyboard_markup.menu_options()
        )

    d_users = Users().to_dict_for_mailing
    await state.update_data(
        message_id=message.message_id,
        forward_from=message.from_user.id,
        page=1,
        d_users=d_users,
    )
    await message.answer(
        text=get_text("send_to"),
        reply_markup=keyboard_inline.mail_list_users(list_users=d_users, page_num=1),
    )
    await state.set_state(Admin.select_user)


@main_router.callback_query(
    Admin.select_user,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "mail",
)
async def select_user_mail(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    id_selected_user = query.data.split(":")[2]
    d_users = data["d_users"]
    d_users = update_dict_users(id_selected_user, d_users)
    await state.update_data(d_users=d_users)
    await query.message.edit_reply_markup(
        reply_markup=keyboard_inline.mail_list_users(
            list_users=d_users, page_num=data["page"]
        )
    )


@main_router.callback_query(
    Admin.select_user,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1].in_(["mail_turn_right", "mail_turn_left"]),
)
async def mail_turn(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    q_page = count_page(5, len(data["d_users"]))
    if q_page == 1:
        return
    page = int(query.data.split(":")[-1].split(".")[0])
    if query.data.split(":")[1] == "mail_turn_left":
        page = page - 1 if page > 1 else q_page
    else:
        page = page + 1 if page < q_page else 1
    await state.update_data(page=page)
    await query.message.edit_reply_markup(
        reply_markup=keyboard_inline.mail_list_users(
            list_users=data["d_users"],
            page_num=page,
        ),
    )


@main_router.callback_query(
    Admin.select_user,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "end_choise_user_mail",
)
async def process_end_choise_selects_mail(
    query: CallbackQuery, state: FSMContext
) -> None:
    data = await state.get_data()
    d_users = [i for i in data["d_users"] if i["select"] != False]
    if not d_users:
        return await query.answer(
            text=get_text("no_one_choice_to_mail"), show_alert=True
        )
    message_id = data["message_id"]
    forward_from = data["forward_from"]

    users_mail_got = 0
    users_no_got_mail = []
    while d_users:
        # d_users: list
        try:
            await bot.copy_message(
                chat_id=d_users[-1]["id"],
                from_chat_id=forward_from,
                message_id=message_id,
            )
            d_users.pop()
            users_mail_got+=1
            await sleep(0.3)
        except Exception:
            users_no_got_mail.append(d_users.pop()['fio'])
    await state.set_state(Admin.main)
    users_no_got_mail = ",".join(users_no_got_mail) if users_no_got_mail else 0
    await query.message.delete()
    await query.message.answer(
        text=get_text(
            "mail_stat",
            throw_data={
                "users_mail_got": users_mail_got,
                "users_no_got_mail": users_no_got_mail,
            },
        ),
        reply_markup=keyboard_markup.main_menu_admin()
    )

