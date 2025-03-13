from aiogram.types import InlineKeyboardButton, \
    KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup
from loguru import logger


class MainMenuKeyboard:    
    def main_menu():
        kb = [
            [
                KeyboardButton(text="Редактировать анкету"),
            ],
            [
                KeyboardButton(text="Статистика профиля"),
            ],
            [
                KeyboardButton(text="Опубликовать пост"),
            ],
            [
                KeyboardButton(text="Сообщение разработчикам"),
                KeyboardButton(text="Баланс"),
            ],
        ]

        greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb)
        return greet_kb

    def edit_profile():
        inline_kb = [
            [
                InlineKeyboardButton(text="Изменить портфолио",
                                     callback_data=f"edit_photos"),
                InlineKeyboardButton(text="Изменить имя",
                                     callback_data=f"edit_name"),
            ],
            [
                InlineKeyboardButton(text="Изменить город",
                                     callback_data=f"edit_city"),
                InlineKeyboardButton(text="Изменить телефон",
                                     callback_data=f"edit_phone"),
            ],
            [
                InlineKeyboardButton(text="Изменить информацию о себе",
                                     callback_data=f"edit_about"),
                InlineKeyboardButton(text="Изменить стили",
                                     callback_data=f"edit_styles"),
            ],
            [
                InlineKeyboardButton(text="Изменить фото профиля",
                                     callback_data=f"edit_photo"),
                InlineKeyboardButton(text="Показать анкету",
                                     callback_data=f"show_anket_upate"),
            ]
        ]

        greet_kb = InlineKeyboardMarkup(inline_keyboard=inline_kb)
        return greet_kb

    def show_anket_update():
        inline_kb = [[
            InlineKeyboardButton(text="Показать анкету",
                                 callback_data=f"show_anket_upate"),
        ]]

        greet_kb = InlineKeyboardMarkup(inline_keyboard=inline_kb)
        return greet_kb

    def tech_link(url: str):
        inline_kb = [[
            InlineKeyboardButton(text="Связаться с тех поддержкой",
                                 url=url),
        ]]

        greet_kb = InlineKeyboardMarkup(inline_keyboard=inline_kb)
        return greet_kb