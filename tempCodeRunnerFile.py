@main_router.message()
@state_is_none
async def all_mes(message: Message, state: FSMContext) -> None:
    id_user = message.from_user.id
    if not flow_db.user_exists(id_user):
        return await command_start(message, state)
    if not flow_db.rule_exists(id_user):
        await  state.set_state(FormReg.fio)
        return await process_fio(message, state)
    rule = flow_db.get(key="rule", where="id", meaning=id_user)
    if rule == "admin":
        await state.set_state(Admin.main)
        return await message.answer(
            get_message_text("again_work"),
            reply_markup=keyboard_markup.main_menu_admin(),
        )
    if rule == "ban":
        return await state.set_state(Ban.void)
    await message.answer(
        get_message_text("again_hello"), reply_markup=keyboard_markup.main_menu_user()
    )