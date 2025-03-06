from aiogram.types import InlineKeyboardButton, \
    InlineKeyboardMarkup
from loguru import logger


class RegisterKeyboards:

    def confirm_master(document_id, update: bool = False):
        inline_kb = [[
            InlineKeyboardButton(
                text="Да", callback_data=f"confirm_master:{'update' if update else ''}|{document_id}|yes"),
            InlineKeyboardButton(
                text="Нет", callback_data=f"confirm_master:{'update' if update else ''}|{document_id}|no"),
        ]]

        greet_kb = InlineKeyboardMarkup(inline_keyboard=inline_kb)
        return greet_kb

    def finish():
        inline_kb = [[
            InlineKeyboardButton(text="Отпраить на проверку",
                                 callback_data=f"finish_registration"),
        ]]

        greet_kb = InlineKeyboardMarkup(inline_keyboard=inline_kb)
        return greet_kb

    def show_styles():
        inline_kb = [[
            InlineKeyboardButton(text="Выбрать стиль из списка",
                                 callback_data=f"show_styles"),
        ]]

        greet_kb = InlineKeyboardMarkup(inline_keyboard=inline_kb)
        return greet_kb

    def show_anket():
        inline_kb = [[
            InlineKeyboardButton(text="Показать анкету",
                                 callback_data=f"show_anket"),
        ]]

        greet_kb = InlineKeyboardMarkup(inline_keyboard=inline_kb)
        return greet_kb

    def create_anket():
        inline_kb = [[
            InlineKeyboardButton(text="Зарегистрироваться",
                                 callback_data=f"create_anket"),
        ]]

        greet_kb = InlineKeyboardMarkup(inline_keyboard=inline_kb)
        return greet_kb
