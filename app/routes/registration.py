import re
from typing import List
from aiogram.filters import Command
from aiogram.types import (Message, CallbackQuery, FSInputFile, ContentType as
                           CT, ReplyKeyboardRemove, BufferedInputFile)
from aiogram.enums import InputMediaType
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from loguru import logger
from service.keyboards.MainMenuKeyboard import MainMenuKeyboard
from service.DAO.AdminDAO import AdminDAO
from service.schemas.Master import Master
from service.schemas.City import CityPydantic
from service.schemas.Style import Style
from service.DAO.StyleDAO import StyleDAO
from service.keyboards.SystemKeyboards import Keyboard
from service.keyboards.RegisterKeyboards import RegisterKeyboards
from utils.utils import bufered_photo, get_master_url, phone_validate
from config import ASSETS_PATH
from utils.pagination.PaginationData import PaginateCallback
from utils.states.Register import Register
from service.keyboards import PaginateKeyboard
from utils.pagination.paginate import Paginator
from service.DAO.CityDAO import CityDAO
from service.DAO.MasterDAO import MasterDAO
import service.texts as texts
from create_bot import bot

router = Router(name="commands")


@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    user: Master = await MasterDAO.get_master_by_tg_id(message.from_user.id)

    if user:
        text = await texts.get_text_from_strapi("welcome_msg")
        await message.answer(text, reply_markup=MainMenuKeyboard.main_menu())
        if not user.validated:
            text = await texts.get_text_from_strapi("welcome_msg_not_confirmed"
                                                    )

            await message.answer(text)
        return

    else:
        text = await texts.get_text_from_strapi("welcome_msg")

        await state.set_state(Register.photos)
        await message.answer_photo(
            FSInputFile(ASSETS_PATH + "/prof_anket.png"),
            caption=text,
            reply_markup=RegisterKeyboards.create_anket(),
        )


@router.callback_query(F.data == "create_anket")
async def create_anket(callback: CallbackQuery, state: FSMContext):
    user: Master = await MasterDAO.get_master_by_tg_id(callback.from_user.id)

    if user:
        text = await texts.get_text_from_strapi(
            "registration_already_registered")
        await callback.message.answer(text)
        return
    text = await texts.get_text_from_strapi("registration_city")
    paginator = Paginator(CityDAO, field='name', keyboard=PaginateKeyboard)
    kb = await paginator.get_kb()
    await state.set_state(Register.city_list)
    await callback.message.delete()
    await callback.message.answer_photo(
        FSInputFile(ASSETS_PATH + "/city.jpg"),
        caption=text,
        reply_markup=kb,
    )


@router.callback_query(Register.city_list, PaginateCallback.filter())
async def city_selected(callback: CallbackQuery,
                        callback_data: PaginateCallback, state: FSMContext):
    paginator = Paginator(CityDAO,
                          'name',
                          callback_data.current,
                          keyboard=PaginateKeyboard)
    documentId = await paginator.process_select(query=callback,
                                                callback_data=callback_data)

    if documentId:
        await state.set_data({"city": documentId})
        await state.set_state(Register.styles)

        text = await texts.get_text_from_strapi("registration_pre_styles")

        await callback.message.answer(
            text, reply_markup=RegisterKeyboards.show_styles())


@router.callback_query(Register.styles, F.data == "show_styles")
async def style_selected(callback: CallbackQuery, state: FSMContext):
    styles: List[Style] = await StyleDAO.get_all()

    text = await texts.get_text_from_strapi("registration_select_styles")
    for i, style in enumerate(styles):
        text += f"\n{i} - {style.style_name}"

    await callback.message.answer(text)
    await state.set_state(Register.styles_apply)


@router.message(Register.styles_apply)
async def set_styles(message: Message, state: FSMContext):
    if not re.match(r'^\d+(\s+\d+)*$', message.text):
        await message.answer(
            "Пожалуйста выберите стили из списка. Пример ввода: 0 1")
        return
    user_styles = message.text.split(' ')
    styles: List[Style] = await StyleDAO.get_all()
    master_styles = []

    for user_style in user_styles:
        master_styles.append(styles[int(user_style)].documentId)

    await state.update_data({"styles": master_styles})
    await state.set_state(Register.phone)
    text = await texts.get_text_from_strapi("registration_phone")
    await message.answer(text=text, reply_markup=Keyboard.send_phone())


@router.message(Register.phone)
async def phone(message: Message, state: FSMContext):
    number = await phone_validate(message=message)

    if number:
        await state.update_data({"phone_number": number})
        await state.set_state(Register.profile_name)

        text = await texts.get_text_from_strapi("registration_profile_name")

        await message.answer(text, reply_markup=ReplyKeyboardRemove())


@router.message(Register.profile_name)
async def profile_name(message: Message, state: FSMContext):
    name = message.text

    await state.update_data({"name": name})
    await state.set_state(Register.main_photo)
    text = await texts.get_text_from_strapi("registration_main_photo")

    await message.answer_photo(FSInputFile(ASSETS_PATH + "/main_photo.png"),
                               caption=text)


@router.message(Register.main_photo, F.content_type.in_([CT.PHOTO]))
async def set_main_photo(message: Message, state: FSMContext):
    if message.photo:
        buffer = await bufered_photo(message.photo[-1].file_id)
    elif message.document:
        buffer = await bufered_photo(message.document.file_id)

    await state.update_data({"profile_image": buffer.read()})
    await state.set_state(Register.photos)
    text = await texts.get_text_from_strapi("registration_photo")
    await message.answer_photo(FSInputFile(ASSETS_PATH + "/photo.jpg"),
                               caption=text)

    await state.set_state(Register.photos)


@router.message(F.content_type.in_([CT.PHOTO]), Register.photos)
async def photos(message: Message,
                 state: FSMContext,
                 album: list[Message] | None = None):
    if album is None:
        text = await texts.get_text_from_strapi("registration_photo_errors")
        await message.answer(text)
        return

    media_group = []
    if album:
        for msg in album:
            obj_dict = msg.model_dump()
            file_id = obj_dict[msg.content_type][-1]['file_id']

            buffered_photo = await bufered_photo(file_id)
            media_group.append(buffered_photo.read())
        await state.update_data({"photos": media_group})

    text = await texts.get_text_from_strapi("registration_about")
    await message.answer(text)

    await state.set_state(Register.about)


@router.message(Register.about)
async def about(message: Message, state: FSMContext):
    if message.text is None:
        return

    await state.update_data({"about_master": message.text})

    # await state.set_state(Register.show_anket)

    text = await texts.get_text_from_strapi("registration_show_anket")
    await state.set_state(Register.finish)
    await message.answer(text, reply_markup=RegisterKeyboards.finish())


@router.callback_query(F.data == "show_anket")
async def show_anket(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    city: CityPydantic = await CityDAO.get_by_document_id(data["city"])

    styles = []
    for style in data["styles"]:
        style_data: Style = await StyleDAO.get_by_document_id(style)
        styles.append(style_data.style_name)

    text = await texts.anket_text(city=city.name,
                                  name=data['name'],
                                  phone=data['phone_number'],
                                  styles=styles,
                                  about=data['about_master'])

    media_group = MediaGroupBuilder(caption="Портфолио")
    for photo in data["photos"]:
        media_group.add(type=InputMediaType.PHOTO,
                        media=BufferedInputFile(photo, "photo_image"))

    await callback.message.answer_media_group(media_group.build())
    await callback.message.answer(text=text)

    await callback.message.answer_photo(
        BufferedInputFile(data["profile_image"], "main_image"),
        caption="Фото профиля:",
        reply_markup=RegisterKeyboards.finish())

    await state.set_state(Register.finish)


@router.callback_query(Register.finish, F.data == "finish_registration")
async def finish_registration(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    data["username"] = callback.from_user.username
    data["master_id"] = callback.from_user.id
    data["master_url"] = get_master_url(callback.from_user)

    master = Master(**data)
    master: Master = await MasterDAO.create_master(master)

    styles = []
    for style in data["styles"]:
        style_data: Style = await StyleDAO.get_by_document_id(style)
        styles.append(style_data.style_name)

    city: CityPydantic = await CityDAO.get_by_document_id(data["city"])

    admins = await AdminDAO.get_admins()
    admin_text = await texts.get_text_from_strapi("registration_admin_text")
    admin_text += f"""
Имя: {data['name']}
Имя пользователя: {data['username']}
Город: {city.name}

Телефон: {data['phone_number']}

Стили: {', '.join(styles)}

О себе: {data['about_master']}

Ссылка на мастера: {data['master_url']}

    """

    for admin in admins:

        media_group = MediaGroupBuilder(caption=admin_text)

        for photo in data["photos"]:
            media_group.add(type=InputMediaType.PHOTO,
                            media=BufferedInputFile(photo, "photo_image"))
        await bot.send_media_group(admin, media_group.build())
        await bot.send_photo(
            admin,
            BufferedInputFile(data["profile_image"], "profile_image"),
            caption="Фото профиля",
            reply_markup=RegisterKeyboards.confirm_master(master.documentId))
    await state.clear()

    await callback.message.delete()
    await callback.message.answer("Анкета отправленна на проверку")
