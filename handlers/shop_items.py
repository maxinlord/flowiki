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
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
import config

from state_classes import Admin
from tool_classes import Item, Items, Reason, User, Users


@main_router.message(Admin.main, F.text == get_button("items"))
async def items_menu(message: Message, state: FSMContext) -> None:
    await state.update_data(page=1)
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
                    "price": item.price_str,
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
                "price": item.price_str,
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
    if Item(data["selected_item"]).photo == "-":
        return await bot.edit_message_text(
            chat_id=query.from_user.id,
            message_id=query.message.message_id,
            text=get_text("menu_items"),
            reply_markup=keyboard_inline.menu_items(page_num=data['page']),
        )
    await bot.delete_message(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
    )
    await bot.send_message(
        chat_id=query.from_user.id,
        text=get_text("menu_items"),
        reply_markup=keyboard_inline.menu_items(page_num=data['page']),
    )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "del_item",
)
async def del_item(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    del Items()[data["selected_item"]]
    await query.message.delete()
    await items_menu(query.message, state)


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "get_qr_code",
)
async def send_qr_code(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer(cache_time=1)
    data = await state.get_data()
    id_item = data["selected_item"]
    item = Item(id_item)
    file_name = f"{item.name}.png"
    await bot.send_document(
        chat_id=query.from_user.id,
        document=FSInputFile(path=item.generate_qr_code(), filename=file_name),
    )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "edit_quantity",
)
async def edit_quantity(query: CallbackQuery, state: FSMContext) -> None:
    await bot.delete_message(
        chat_id=query.from_user.id, message_id=query.message.message_id
    )
    await bot.send_message(
        chat_id=query.from_user.id, text=get_text("enter_num_for_edit_quantity")
    )
    await state.set_state(Admin.enter_num_for_edit_quantity)


@main_router.message(Admin.enter_num_for_edit_quantity)
async def enter_num_for_edit_quantity(message: Message, state: FSMContext) -> None:
    if not message.text.isnumeric():
        return
    data = await state.get_data()
    item = Item(data["selected_item"])
    item.quantity = message.text
    await state.set_state(Admin.main)
    if item.photo == "-":
        return await message.answer(
            text=get_text(
                "item_parametrs",
                throw_data={
                    "name": item.name,
                    "description": item.description,
                    "price": item.price_str,
                    "quantity": item.quantity,
                },
            ),
            reply_markup=keyboard_inline.option_item(),
        )
    await message.answer_photo(
        photo=item.photo,
        caption=get_text(
            "item_parametrs",
            throw_data={
                "name": item.name,
                "description": item.description,
                "price": item.price_str,
                "quantity": item.quantity,
            },
        ),
        reply_markup=keyboard_inline.option_item(),
    )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "edit_price",
)
async def edit_price(query: CallbackQuery, state: FSMContext) -> None:
    await bot.delete_message(
        chat_id=query.from_user.id, message_id=query.message.message_id
    )
    await bot.send_message(
        chat_id=query.from_user.id, text=get_text("enter_num_for_edit_price")
    )
    await state.set_state(Admin.enter_num_for_edit_price)


@main_router.message(Admin.enter_num_for_edit_price)
async def get_num_for_edit_price_item(message: Message, state: FSMContext) -> None:
    if not message.text.isnumeric():
        return
    data = await state.get_data()
    item = Item(data["selected_item"])
    item.price = message.text
    await state.set_state(Admin.main)
    if item.photo == "-":
        return await message.answer(
            text=get_text(
                "item_parametrs",
                throw_data={
                    "name": item.name,
                    "description": item.description,
                    "price": item.price_str,
                    "quantity": item.quantity,
                },
            ),
            reply_markup=keyboard_inline.option_item(),
        )
    await message.answer_photo(
        photo=item.photo,
        caption=get_text(
            "item_parametrs",
            throw_data={
                "name": item.name,
                "description": item.description,
                "price": item.price_str,
                "quantity": item.quantity,
            },
        ),
        reply_markup=keyboard_inline.option_item(),
    )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "reset_old_price",
)
async def reset_old_price(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    item = Item(data["selected_item"])
    item.old_price = 0
    if item.photo == "-":
        return await bot.edit_message_text(
            chat_id=query.from_user.id,
            message_id=query.message.message_id,
            text=get_text(
                "item_parametrs",
                throw_data={
                    "name": item.name,
                    "description": item.description,
                    "price": item.price_str,
                    "quantity": item.quantity,
                },
            ),
            reply_markup=keyboard_inline.option_item(),
        )
    await bot.edit_message_caption(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        caption=get_text(
            "item_parametrs",
            throw_data={
                "name": item.name,
                "description": item.description,
                "price": item.price_str,
                "quantity": item.quantity,
            },
        ),
        reply_markup=keyboard_inline.option_item(),
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
    await query.message.edit_text(text=get_text("item_created"), reply_markup=None)
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


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1].in_(["item_turn_left", "item_turn_right"]),
)
async def item_turn(query: CallbackQuery, state: FSMContext) -> None:
    items = Items()
    q_page = count_page(5, len(items))
    page = int(float(query.data.split(":")[-1]))
    if query.data.split(":")[1] == "item_turn_right":
        page = page + 1 if page < q_page else 1
    else:
        page = page - 1 if page > 1 else q_page
    await state.update_data(page=page)
    await query.message.edit_reply_markup(reply_markup=keyboard_inline.menu_items(page_num=page))
