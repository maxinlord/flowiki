from aiogram import F
from own_utils import (
    activate_preset,
    count_page,
    create_tag_for_notify,
    create_tag_for_preset,
    de_active_presets,
    delete_notification,
    delete_preset,
    extract_date,
    extract_time,
    get_button,
    get_dict_users,
    get_text,
    unwrap_2dd,
    update_dict_users,
    wrap_2dd,
    weekday_tr
)
from dispatcher import main_router, bot
import keyboard_inline, keyboard_markup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from init_db import flow_db
from state_classes import Admin


@main_router.message(Admin.main, F.text == get_button("notifications"))
async def notifications_admin(message: Message, state: FSMContext) -> None:
    user_notifications = flow_db.parse_2dd(
        table="users", key="notifications", where="id", meaning=message.from_user.id
    )
    user_notifications = [
        notify for notify in user_notifications if notify["is_active"] == 1
    ]
    await state.update_data(user_notifications=user_notifications)
    await message.answer(
        text=get_text("menu_notification"),
        reply_markup=keyboard_inline.menu_notifications(user_notifications),
    )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "tap_on_notify",
)
async def tap_on_notify(query: CallbackQuery, state: FSMContext) -> None:
    id_notify = query.data.split(":")[-1]
    await state.update_data(selected_notify=id_notify)
    notifications = flow_db.parse_2dd(
        table="users",
        key="notifications",
        where="id",
        meaning=query.from_user.id
    )
    current_notify = [notify for notify in notifications if id_notify == notify['id_notify']][0]
    await bot.edit_message_text(
        text=get_text(
            "your_message_to_remind", throw_data={
                "message": unwrap_2dd(current_notify['message']),
                'time': unwrap_2dd(current_notify['time']),
                'weekday': weekday_tr[current_notify['weekday']]}
        ),
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.back_and_del_notify(),
    )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "back_to_menu_notifications",
)
async def back_to_menu_notifications(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        text=get_text("menu_notification"),
        reply_markup=keyboard_inline.menu_notifications(data["user_notifications"]),
    )


@main_router.callback_query(
    Admin.main, F.data.split(":")[0] == "action", F.data.split(":")[1] == "del_notify"
)
async def del_notify(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    id_notify = data["selected_notify"]
    user_notifications = data["user_notifications"]
    user_notifications = delete_notification(user_notifications, id_notify)
    await state.update_data(user_notifications=user_notifications)
    flow_db.update_value_2dd(
        table="users",
        key="notifications",
        where="id",
        meaning=query.from_user.id,
        where_data="id_notify",
        meaning_data=id_notify,
        update_data="is_active",
        value="0",
    )
    await bot.edit_message_text(
        text=get_text("menu_notification"),
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.menu_notifications(user_notifications),
    )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "add_new_notify",
)
async def add_new_notify(query: CallbackQuery, state: FSMContext) -> None:
    await bot.delete_message(
        message_id=query.message.message_id,
        chat_id=query.from_user.id,
    )
    await bot.send_message(
        text=get_text("choise_type_notify"),
        chat_id=query.from_user.id,
        reply_markup=keyboard_inline.type_notify(),
    )
    await state.update_data(weekday='monday')
    await state.set_state(Admin.choise_type_notify)


@main_router.callback_query(
    Admin.choise_type_notify,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "tap_on_type",
)
async def choose_type_notify(query: CallbackQuery, state: FSMContext) -> None:
    type_ = query.data.split(":")[-1]
    await state.update_data(type_notify=type_)
    if type_ == "once":
        await bot.edit_message_text(
            chat_id=query.from_user.id,
            message_id=query.message.message_id,
            text=get_text("enter_time_notify_once"),
            reply_markup=None,
        )
        await state.set_state(Admin.enter_time_notify_once)
        return
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        text=get_text("choise_day"),
        reply_markup=keyboard_inline.week_days(),
    )
    await state.set_state(Admin.choise_day_notify)


@main_router.callback_query(
    Admin.choise_day_notify,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "tap_on_day",
)
async def choose_day_notify(query: CallbackQuery, state: FSMContext) -> None:
    day = query.data.split(":")[-1]
    await state.update_data(weekday=day)
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        text=get_text("enter_time_notify_remind"),
        reply_markup=None,
    )
    await state.set_state(Admin.enter_time_notify_remind)


@main_router.message(Admin.enter_time_notify_once)
async def get_time_notify(message: Message, state: FSMContext) -> None:
    # sourcery skip: de-morgan, merge-duplicate-blocks, reintroduce-else, remove-redundant-if, split-or-ifs, swap-if-else-branches
    date = extract_date(message.text)
    time = extract_time(message.text)
    if not (date and time):
        return await message.answer(text=get_text("not_found_date_or_time"))
    date_and_time = f"{date[0]} {time}".strip()
    await state.update_data(time=date_and_time, weekday=date[1])
    await message.answer(
        text=get_text("time_set_on", throw_data={"time": date_and_time})
    )
    await message.answer(text=get_text("enter_message_to_remind"))
    await state.set_state(Admin.enter_message_to_remind)


@main_router.message(Admin.enter_time_notify_remind)
async def get_time_notify(message: Message, state: FSMContext) -> None:
    time = extract_time(message.text)
    if not time:
        return await message.answer(text=get_text("not_found_date_or_time"))
    await state.update_data(time=time.strip())
    await message.answer(
        text=get_text("time_set_on", throw_data={"time": time})
    )
    await message.answer(text=get_text("enter_message_to_remind"))
    await state.set_state(Admin.enter_message_to_remind)


@main_router.message(Admin.enter_message_to_remind)
async def get_message_to_remind(message: Message, state: FSMContext) -> None:
    await state.update_data(message_to_remind=message.text)
    await message.answer(text=get_text("message_writed"))
    user_presets = flow_db.parse_2dd(
        table="users", key="presets", where="id", meaning=message.from_user.id
    )
    await message.answer(
        text=get_text("choice_preset_for_flownomika"),
        reply_markup=keyboard_inline.menu_presets_for_notify(user_presets),
    )
    await state.set_state(Admin.choice_preset_for_flownomika)


@main_router.callback_query(
    Admin.choice_preset_for_flownomika,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "tap_on_preset",
)
async def tap_on_preset_notify(query: CallbackQuery, state: FSMContext) -> None:
    id_preset = query.data.split(":")[-1]
    data = await state.get_data()
    flow_db.add_2dd(
        table="users",
        key="notifications",
        where="id",
        meaning=query.from_user.id,
        throw_data=[
            create_tag_for_notify(),
            data['type_notify'],
            data['weekday'],
            wrap_2dd(data["time"]),
            wrap_2dd(data["message_to_remind"]),
            id_preset,
            "1",
        ],
    )
    await state.set_state(Admin.main)
    await bot.delete_message(
        chat_id=query.from_user.id, message_id=query.message.message_id
    )
    await bot.send_message(
        chat_id=query.from_user.id,
        text=get_text("notify_created"),
        reply_markup=keyboard_markup.menu_options(),
    )
