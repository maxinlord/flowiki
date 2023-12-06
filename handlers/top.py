from aiogram import F
from own_utils import (
    get_button,
    get_text,
    wrap,
)
from dispatcher import main_router
from init_db import flow_db
from aiogram.types import Message
from aiogram.fsm.context import FSMContext


@main_router.message(F.text == get_button("top"))
async def top_flow(message: Message, state: FSMContext) -> None:
    raw_data = flow_db.get_all_line_key(
        key="fio, balance_flow, rule", order="balance_flow"
    )
    place, tops = 1, []
    for i in raw_data:
        if i["rule"] == "admin":
            continue
        tops.append(
            get_text(
                "pattern_line_top",
                throw_data={
                    "fio": i["fio"],
                    "balance": wrap(i["balance_flow"]),
                    "place": place,
                },
            )
        )
        place += 1
    tops_text = "\n".join(tops)
    await message.answer(get_text("top_info", throw_data={"list_top": tops_text}))