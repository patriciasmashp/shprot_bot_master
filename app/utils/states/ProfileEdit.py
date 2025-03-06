from aiogram.fsm.state import StatesGroup, State


class ProfileEdit(StatesGroup):
    city_list = State()
    about = State()
    phone = State()
    styles = State()
    styles_apply = State()
    photos = State()
    main_photo = State()
    profile_name = State()
    show_anket = State()
    finish = State()
    
    reason_refusal = State()