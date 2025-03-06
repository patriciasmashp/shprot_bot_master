from aiogram.types import InlineKeyboardButton, \
    InlineKeyboardMarkup, \
    KeyboardButton, \
    ReplyKeyboardMarkup
from loguru import logger



class Keyboard():

    def main_menu_kb(admin: bool = False):
        kb = [
            [KeyboardButton(text="Ассортимент")],
            [KeyboardButton(text="Ассортимент ")],
        ]
        if admin:
            kb.append([KeyboardButton(text="Админ панель")])

        greet_kb = ReplyKeyboardMarkup(resize_keyboard=False, keyboard=kb)
        return greet_kb

    def send_phone():
        kb = [
            [
                KeyboardButton(text="Отправить номер телефона",
                               request_contact=True)
            ],
        ]

        greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb)
        return greet_kb

    def starts():
        inline_kb = [[
            InlineKeyboardButton(text="1️⃣", callback_data=f"1"),
            InlineKeyboardButton(text="2️⃣", callback_data=f"2"),
            InlineKeyboardButton(text="3️⃣", callback_data=f"3"),
            InlineKeyboardButton(text="4️⃣", callback_data=f"4"),
            InlineKeyboardButton(text="5️⃣", callback_data=f"5")
        ]]

        greet_kb = InlineKeyboardMarkup(inline_keyboard=inline_kb)
        return greet_kb

    def y_n_kb():
        inline_kb = [[
            InlineKeyboardButton(text="Да", callback_data="y"),
            InlineKeyboardButton(text="Нет", callback_data="n"),
        ]]

        greet_kb = InlineKeyboardMarkup(inline_keyboard=inline_kb)
        return greet_kb

    def back():
        inline_kb = [
            [InlineKeyboardButton(text="Назад", callback_data=f"back")],
        ]

        greet_kb = InlineKeyboardMarkup(inline_keyboard=inline_kb)
        return greet_kb

    def delete_button():
        inline_kb = [[
            InlineKeyboardButton(text="Удалить", callback_data=f"delete")
        ]]

        greet_kb = InlineKeyboardMarkup(inline_keyboard=inline_kb)
        return greet_kb
