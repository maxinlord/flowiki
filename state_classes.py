from aiogram.fsm.state import State, StatesGroup


class FormReg(StatesGroup):
    fio = State()
    pending_review = State()
    hand_reg = State()


class Admin(StatesGroup):
    main = State()
    flownomika = State()
    enter_reason = State()
    enter_another_quantity = State()
    enter_name_preset = State()
    enter_time_notify = State()
    enter_message_to_remind = State()
    choice_preset_for_flownomika = State()


class Viewer(StatesGroup):
    main = State()


class Ban(StatesGroup):
    void = State()
