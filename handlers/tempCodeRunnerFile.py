@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1].in_(["buy_item_turn_left", "buy_item_turn_right"]),
)
async def buy_item_turn(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    q_page = count_page(5, len(data["buy_item_users"]))
    if q_page == 1:
        return
    page = int(query.data.split(":")[-1].split(".")[0])
    if query.data.split(":")[1] == "preset_turn_left":
        page = page - 1 if page > 1 else q_page
    else:
        page = page + 1 if page < q_page else 1
    await query.message.edit_reply_markup(
        reply_markup=keyboard_inline.buy_item_list_users(
            list_users=data["buy_item_users"],
            page_num=page,
        ),
    )