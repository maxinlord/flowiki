import contextlib
import os
from aiogram import F
from own_utils import (
    get_text,
    get_xlsx_table,
    is_xlsx_extend,
    write_excel_to_db,
)
from dispatcher import main_router, bot
from init_db import flow_db
import keyboard_inline
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from state_classes import Admin
from aiogram.types import FSInputFile


@main_router.message(Admin.main, F.text == "file")
async def get_file(message: Message):
    await message.answer(get_text("files"), reply_markup=keyboard_inline.get_files_k())
    # get_xlsx_table(flow_db.conn, 'users')
    # await message.answer_document(document=open('users.xlsx', 'rb'))


@main_router.callback_query(Admin.main, F.data.split(":")[0] == "name_table")
async def answer_button(call: CallbackQuery, state: FSMContext):
    name_table = call.data.split(":")[1]
    get_xlsx_table(flow_db.conn, f"{name_table}")
    # with open(f'{name_table}.xlsx', 'rb') as file:
    await bot.send_document(
        chat_id=call.from_user.id, document=FSInputFile(f"{name_table}.xlsx")
    )


@main_router.message(Admin.main, F.document)
async def handle_docs(message: Message):
    file_name = message.document.file_name
    if is_xlsx_extend(file_name):
        flow_db.close(flow_db.conn)
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        with contextlib.suppress(Exception):
            os.remove(f"{file_name}")
        await bot.download_file(file.file_path, f"{file_name}")
        conn, cur = flow_db.create_new_connection()
        write_excel_to_db(excel_file=file_name, conn=conn)
        flow_db.conn, flow_db.cur = conn, cur
        return await message.answer(get_text("handle_docs.done"))
    await message.answer(get_text("handle_docs.error"))


# @main_router.message(Command("update"))
# async def update(message: Message, state: FSMContext) -> None:
#     await all_mes(message, state)
