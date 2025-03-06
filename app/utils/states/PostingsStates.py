from aiogram.fsm.state import StatesGroup, State


class Posting(StatesGroup):
    type_of_post = State()
    files_upload = State()
    price = State()

    # SKETCH
    body_part = State()

    sessions = State()
    
    # PHOTO
    style = State()

    # FINAL
    confirm = State()

    social = State()
