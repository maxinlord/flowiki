from aiogram import F
from own_utils import (
    count_page,
    get_button,
    get_current_date,
    get_text,
    update_dict_users,
    view_selected_users,
    wrap,
)
from dispatcher import main_router, bot
import keyboard_inline, keyboard_markup
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import config

from state_classes import Admin
from tool_classes import Item, Items, Reason, User, Users


@main_router.message(Admin.main, F.text == get_button("items"))
async def notifications_admin(message: Message, state: FSMContext) -> None:
    await message.answer(
        text=get_text("menu_items"),
        reply_markup=keyboard_inline.menu_items(),
    )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "tap_on_item",
)
async def tap_on_item(query: CallbackQuery, state: FSMContext) -> None:
    item = Item(query.data.split(":")[-1])
    await state.update_data(selected_item=item.id_item)
    if item.photo == "-":
        return await bot.edit_message_text(
            chat_id=query.from_user.id,
            message_id=query.message.message_id,
            text=get_text(
                "item_parametrs",
                throw_data={
                    "name": item.name,
                    "description": item.description,
                    "price": item.price,
                    "quantity": item.quantity,
                },
            ),
            reply_markup=keyboard_inline.option_item(),
        )
    await bot.delete_message(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
    )
    await bot.send_photo(
        chat_id=query.from_user.id,
        photo=item.photo,
        caption=get_text(
            "item_parametrs",
            throw_data={
                "name": item.name,
                "description": item.description,
                "price": item.price,
                "quantity": item.quantity,
            },
        ),
        reply_markup=keyboard_inline.option_item(),
    )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "back_to_menu_item",
)
async def back_to_menu_item(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    if Item(data['selected_item']).photo == '-':
        return await bot.edit_message_text(
            chat_id=query.from_user.id,
            message_id=query.message.message_id,
            text=get_text('menu_items'),
            reply_markup=keyboard_inline.menu_items(),
        )
    await bot.delete_message(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
    )
    await bot.send_message(
            chat_id=query.from_user.id,
            text=get_text('menu_items'),
            reply_markup=keyboard_inline.menu_items(),
        )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "add_item",
)
async def add_item(query: CallbackQuery, state: FSMContext) -> None:
    await bot.edit_message_text(
        text=get_text("enter_name_item"),
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
    )
    await state.set_state(Admin.enter_name_item)


@main_router.message(Admin.enter_name_item)
async def get_name_item(message: Message, state: FSMContext) -> None:
    name = message.text
    await state.update_data(name_item=name)
    await message.answer(
        text=get_text("enter_description_item"),
    )
    await state.set_state(Admin.enter_description_item)


@main_router.message(Admin.enter_description_item)
async def get_description_item(message: Message, state: FSMContext) -> None:
    description = message.text
    await state.update_data(description_item=description)
    await message.answer(
        text=get_text("enter_price_item"),
    )
    await state.set_state(Admin.enter_price_item)


@main_router.message(Admin.enter_price_item)
async def get_price_item(message: Message, state: FSMContext) -> None:
    if not message.text.isnumeric():
        return
    price = message.text
    await state.update_data(price_item=price)
    await message.answer(
        text=get_text("enter_quantity_item"),
    )
    await state.set_state(Admin.enter_quantity_item)


@main_router.message(Admin.enter_quantity_item)
async def get_quantity_item(message: Message, state: FSMContext) -> None:
    if not message.text.isnumeric():
        return
    quantity = message.text
    await state.update_data(quantity_item=quantity)
    await message.answer(
        text=get_text("send_photo_item"), reply_markup=keyboard_inline.skip_photo()
    )
    await state.set_state(Admin.send_photo_item)


@main_router.callback_query(
    Admin.send_photo_item,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "skip_photo",
)
async def end_create_item(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    item = Items()["new_item"]
    item.name = data["name_item"]
    item.description = data["description_item"]
    item.price = data["price_item"]
    item.quantity = data["quantity_item"]
    await bot.send_message(
        chat_id=query.from_user.id,
        text=get_text("item_created"),
    )
    await state.set_state(Admin.main)


@main_router.message(Admin.send_photo_item, F.photo)
async def get_photo_item(message: Message, state: FSMContext) -> None:
    photo_id = message.photo[-1].file_id
    data = await state.get_data()
    item = Items()["new_item"]
    item.name = data["name_item"]
    item.description = data["description_item"]
    item.price = data["price_item"]
    item.quantity = data["quantity_item"]
    item.photo = photo_id
    await message.answer(
        text=get_text("item_created"),
    )
    await state.set_state(Admin.main)
