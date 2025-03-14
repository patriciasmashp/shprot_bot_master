from typing import List
from aiogram.types import InlineKeyboardButton, \
    KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup
from loguru import logger


class PostingKeyboard:
    def after_help():
        inline_kb = [[
            InlineKeyboardButton(text="Опубликовать пост",
                                 callback_data="start_post"),
        ]]

        greet_kb = InlineKeyboardMarkup(inline_keyboard=inline_kb)
        return greet_kb
    
    def show_post():
        inline_kb = [[
            InlineKeyboardButton(text="Показать пост", callback_data="confirm")
        ]]

        greet_kb = InlineKeyboardMarkup(inline_keyboard=inline_kb)
        return greet_kb

    def confirm():
        inline_kb = [[
            InlineKeyboardButton(text="Отправить на проверку",
                                 callback_data="send"),
            InlineKeyboardButton(text="Начать заново",
                                 callback_data="restart"),
        ]]

        greet_kb = InlineKeyboardMarkup(inline_keyboard=inline_kb)
        return greet_kb

    def socials():
        inline_kb = [[
            InlineKeyboardButton(text="ВКонтакте", callback_data="vk"),
            InlineKeyboardButton(text="Instagram", callback_data="ig"),
        ]]

        greet_kb = InlineKeyboardMarkup(inline_keyboard=inline_kb)
        return greet_kb

    def type_of_post():
        inline_kb = [
            [InlineKeyboardButton(text="Эскиз", callback_data="sketch")],
            [InlineKeyboardButton(text="Фото работы", callback_data="photo")],
            [InlineKeyboardButton(text="Видео", callback_data="video")],
            [
                InlineKeyboardButton(text="Зачем это нужно",
                                     callback_data="help")
            ]
        ]

        greet_kb = InlineKeyboardMarkup(inline_keyboard=inline_kb)
        return greet_kb

    def y_n_kb(document_id: str, media_message_id: List[str], social: str):
        ids_data = ','.join(media_message_id)
        
        # ? в callback_data передается статус ответа, id мастера, ключи изображений в s3 и соц. сеть
        inline_kb = [[
            InlineKeyboardButton(text="Да", callback_data=f"post|y|{document_id}|{ids_data}|{social}"),
            InlineKeyboardButton(text="Нет", callback_data=f"post|n|{document_id}|{ids_data}|{social}"),
        ]]

        greet_kb = InlineKeyboardMarkup(inline_keyboard=inline_kb)
        return greet_kb