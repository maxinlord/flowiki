from aiogram import F
from own_utils import (
    delete_notification,
    extract_date,
    extract_time,
    get_button,
    get_text
)
from dispatcher import main_router, bot
import keyboard_inline, keyboard_markup
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from state_classes import Admin
from tool_classes import Notification, Preset, User


@main_router.message(Admin.main, F.text == get_button("notifications"))
async def notifications_admin(message: Message, state: FSMContext) -> None:
    user = User(message.from_user.id)
    await state.update_data(user_notifications=list(user.notification))
    await message.answer(
        text=get_text("menu_notification"),
        reply_markup=keyboard_inline.menu_notifications(list(user.notification), user.id),
    )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "tap_on_notify",
)
async def tap_on_notify(query: CallbackQuery, state: FSMContext) -> None:
    id_notify = query.data.split(":")[-1]
    notify = User(query.from_user.id).notification
    notify.id_notify = id_notify
    await state.update_data(selected_notify=id_notify)
    await bot.edit_message_text(
        text=get_text(
            "your_message_to_remind", throw_data={
                "message": notify.message,
                'time': notify.time,
                'weekday': notify.weekday}
        ),
        chat_id=notify.id_user,
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
        reply_markup=keyboard_inline.menu_notifications(data["user_notifications"], query.from_user.id),
    )


@main_router.callback_query(
    Admin.main, F.data.split(":")[0] == "action", F.data.split(":")[1] == "del_notify"
)
async def del_notify(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    id_notify = data["selected_notify"]
    notify = User(query.from_user.id).notification
    user_notifications = data["user_notifications"]
    user_notifications = delete_notification(user_notifications, id_notify)
    await state.update_data(user_notifications=user_notifications)
    del notify[id_notify]
    await bot.edit_message_text(
        text=get_text("menu_notification"),
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.menu_notifications(user_notifications, query.from_user.id),
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
    preset = Preset(message.from_user.id)
    await message.answer(
        text=get_text("choice_preset_for_flownomika"),
        reply_markup=keyboard_inline.menu_presets_for_notify(list(preset)),
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
    notify = Notification(query.from_user.id)
    notify.create_notify
    notify.type_notify = data['type_notify']
    notify.weekday = data['weekday']
    notify.time = data["time"]
    notify.message = data["message_to_remind"]
    notify.id_preset = id_preset
    notify.is_active = 1

    await state.set_state(Admin.main)
    await bot.delete_message(
        chat_id=query.from_user.id, message_id=query.message.message_id
    )
    await bot.send_message(
        chat_id=notify.id_user,
        text=get_text("notify_created"),
        reply_markup=keyboard_markup.menu_options(),
    )
