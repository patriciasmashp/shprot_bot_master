import io
import re
from loguru import logger
from service.BaseApi.StrapiApi import StrapiApi
from service import texts
from config import BASE_PATH
from service.keyboards.SystemKeyboards import Keyboard
from create_bot import dp
from PIL import Image
import os
import importlib.util
from create_bot import bot
from aiogram.types.message import Message
from aiogram.types.user import User as TgUser


def register_routers():
    # Путь к папке с файлами
    routes_folder = 'routes'

    # Список для хранения всех переменных route
    all_routes = []

    # Проходимся по всем файлам в папке
    for filename in os.listdir(routes_folder):
        if filename.endswith('.py'):
            file_path = os.path.join(routes_folder, filename)

            # Импортируем модуль
            spec = importlib.util.spec_from_file_location(
                filename[:-3], file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Получаем переменную route, если она существует
            if hasattr(module, 'router'):
                all_routes.append(module.router)

    # Вывод всех найденных переменных route
    for router in all_routes:
        dp.include_router(router)


async def download_photo(file_id):
    file = await bot.get_file(file_id)
    ext = file.file_path.split(".")[1]
    path = BASE_PATH + "\\images\\" + file_id + "." + ext

    await bot.download_file(file.file_path, path)

    return path


async def bufered_photo(file_id):
    file = await bot.get_file(file_id)
    # ext = file.file_path.split(".")[1]
    # path = BASE_PATH + "\\images\\" + file_id + "." + ext
    ioBuffer = io.BytesIO()
    await bot.download_file(file.file_path, ioBuffer)
    return ioBuffer


async def phone_validate(message: Message,
                         message_key: str = "registration_phone"):
    if message.contact is not None:
        number = message.contact.phone_number
    else:
        number = message.text
        result = re.match(
            r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$',
            number)
        if result is None:
            kb = Keyboard.send_phone()
            text = await texts.get_text_from_strapi(message_key)
            await message.answer(text, reply_markup=kb)

            return None

    return number


def get_master_url(user):
    if user.username is None:
        return f"https://t.me/{user.id}"
    else:
        return f"https://t.me/{user.username}"


def resize_image(image, size: tuple):
    im = Image.open(image)
    im = im.resize(size)
    ioBuffer = io.BytesIO()
    logger.debug(im.size)

    im.save(ioBuffer, "JPEG")
    ioBuffer.seek(0)
    return ioBuffer


async def check_media_requirements(media, m_type):
    errors = {}
    if m_type == "video":
        if 15 < media.duration < 60:
            text = await texts.get_text_from_strapi("post_error_video_duration"
                                                    )
            errors.update({"duration": text})
    logger.debug(media.height)
    logger.debug(media.width)
    
    if media.height not in [566, 1350, 1080] or media.width not in [1080, 1350]:
        text = await texts.get_text_from_strapi("post_error_media_sizes"
                                                )
        errors.update({"dimesions": text})
        
    if len(errors) == 0:
        return True
    return errors