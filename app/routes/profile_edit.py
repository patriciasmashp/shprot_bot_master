from typing import List
from aiogram import F, Router
from aiogram.types import (Message, CallbackQuery, ContentType as CT,
                           URLInputFile, ReplyKeyboardRemove)
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.enums import InputMediaType
from aiogram.exceptions import TelegramNetworkError
from loguru import logger

from service.DAO.StyleDAO import StyleDAO
from service.schemas.Style import Style
from service.keyboards.SystemKeyboards import Keyboard
from service.DAO.CityDAO import CityDAO
from service.keyboards.PaginateKeyboard import PaginateKeyboard
from utils.pagination.PaginationData import PaginateCallback
from utils.pagination.paginate import Paginator
from service.DAO.AdminDAO import AdminDAO
from service.schemas.City import CityPydantic
from config import STRAPI_MEDIA_URL
from service.keyboards.RegisterKeyboards import RegisterKeyboards
from utils.utils import bufered_photo, get_master_url, phone_validate
from utils.states.ProfileEdit import ProfileEdit
from service import texts
from service.keyboards.MainMenuKeyboard import MainMenuKeyboard
from service.schemas.Master import Master
from service.DAO.MasterDAO import MasterDAO
from create_bot import bot

router = Router(name="profile_edit")


@router.callback_query(F.data == "edit_photo")
async def edit_photo(callback: CallbackQuery, state: FSMContext):
    text = await texts.get_text_from_strapi("registration_main_photo")
    await state.set_state(ProfileEdit.main_photo)
    await callback.message.answer(text=text)


@router.message(ProfileEdit.main_photo, F.content_type.in_([CT.PHOTO]))
async def set_main_photo(message: Message, state: FSMContext):
    if message.photo:
        buffer = await bufered_photo(message.photo[-1].file_id)
    elif message.document:
        buffer = await bufered_photo(message.document.file_id)

    master: Master = await MasterDAO.get_master_by_tg_id(message.from_user.id)
    master.validated = None
    await MasterDAO.update_master(master.to_upload(), master.documentId)
    await MasterDAO.update_main_photo(master.documentId, buffer.read())

    text = await texts.get_text_from_strapi("registration_show_anket")
    await message.answer(text,
                         reply_markup=MainMenuKeyboard.show_anket_update())


@router.callback_query(F.data == "edit_styles")
async def edit_styles(callback: CallbackQuery, state: FSMContext):
    text = await texts.get_text_from_strapi("registration_select_styles")

    styles: List[Style] = await StyleDAO.get_all()

    for i, style in enumerate(styles):
        text += f"\n{i} - {style.style_name}"
    await state.set_state(ProfileEdit.styles_apply)
    await callback.message.answer(text=text)


@router.message(ProfileEdit.styles_apply)
async def set_styles(message: Message, state: FSMContext):
    user_styles = message.text.split(' ')
    styles: List[Style] = await StyleDAO.get_all()
    master_styles = []

    for user_style in user_styles:
        master_styles.append(styles[int(user_style)].documentId)

    master: Master = await MasterDAO.get_master_by_tg_id(message.from_user.id)

    master.styles = master_styles
    master.validated = None
    await MasterDAO.update_master(master.to_upload(), master.documentId)

    text = await texts.get_text_from_strapi("registration_show_anket")
    await message.answer(text,
                         reply_markup=MainMenuKeyboard.show_anket_update())


@router.callback_query(F.data == "edit_about")
async def edit_about(callback: CallbackQuery, state: FSMContext):
    text = await texts.get_text_from_strapi("registration_about")
    await state.set_state(ProfileEdit.about)
    await callback.message.answer(text=text)


@router.message(ProfileEdit.about)
async def about(message: Message, state: FSMContext):
    about = message.text
    master: Master = await MasterDAO.get_master_by_tg_id(message.from_user.id,
                                                         populate=True)

    master.about_master = about
    master.validated = None

    await MasterDAO.update_master(master.to_upload(), master.documentId)

    text = await texts.get_text_from_strapi("registration_show_anket")
    await message.answer(text,
                         reply_markup=MainMenuKeyboard.show_anket_update())


@router.callback_query(F.data == "edit_phone")
async def edit_phone(callback: CallbackQuery, state: FSMContext):
    text = await texts.get_text_from_strapi("registration_phone")
    await state.set_state(ProfileEdit.phone)
    await callback.message.answer(text=text,
                                  reply_markup=Keyboard.send_phone())


@router.message(ProfileEdit.phone)
async def phone(message: Message, state: FSMContext):
    number = await phone_validate(message=message)

    if number:
        master: Master = await MasterDAO.get_master_by_tg_id(
            message.from_user.id, populate=True)

        master.phone_number = number
        master.validated = None
        await MasterDAO.update_master(master.to_upload(), master.documentId)

        text = "Успешно"
        await message.answer(text, reply_markup=MainMenuKeyboard.main_menu())
        text = await texts.get_text_from_strapi("registration_show_anket")
        await message.answer(text,
                             reply_markup=MainMenuKeyboard.show_anket_update())


@router.callback_query(F.data == "edit_city")
async def edit_sity(callback: CallbackQuery, state: FSMContext):
    text = await texts.get_text_from_strapi("registration_city")
    paginator = Paginator(CityDAO, field='name', keyboard=PaginateKeyboard)
    kb = await paginator.get_kb()
    await state.set_state(ProfileEdit.city_list)
    await callback.message.edit_text(
        text=text,
        reply_markup=kb,
    )


@router.callback_query(ProfileEdit.city_list, PaginateCallback.filter())
async def city_selected(callback: CallbackQuery,
                        callback_data: PaginateCallback, state: FSMContext):
    paginator = Paginator(CityDAO,
                          'name',
                          callback_data.current,
                          keyboard=PaginateKeyboard)
    documentId = await paginator.process_select(query=callback,
                                                callback_data=callback_data)

    if documentId:
        master: Master = await MasterDAO.get_master_by_tg_id(
            callback.from_user.id, populate=True)
        master.validated = False
        await MasterDAO.update_master(master.to_upload(), master.documentId)
        await MasterDAO.update_city(master.documentId, documentId)

        text = await texts.get_text_from_strapi("registration_show_anket")
        await callback.message.answer(
            text, reply_markup=MainMenuKeyboard.show_anket_update())


@router.callback_query(F.data == "edit_name")
async def edit_profile(callback: CallbackQuery, state: FSMContext):
    text = await texts.get_text_from_strapi("registration_profile_name")
    await state.set_state(ProfileEdit.profile_name)
    await callback.message.edit_text(text=text)


@router.message(ProfileEdit.profile_name)
async def edit_profile_name(message: Message, state: FSMContext):
    master: Master = await MasterDAO.get_master_by_tg_id(message.from_user.id,
                                                         populate=True)
    master.name = message.text
    master.validated = False

    await MasterDAO.update_master(master, master.documentId)

    text = await texts.get_text_from_strapi("registration_show_anket")

    await message.answer(text,
                         reply_markup=MainMenuKeyboard.show_anket_update())


@router.callback_query(F.data == "edit_photos")
async def edit_pphotos(callback: CallbackQuery, state: FSMContext):
    text = await texts.get_text_from_strapi("registration_photo")
    await state.set_state(ProfileEdit.photos)
    await callback.message.edit_text(text=text)


@router.message(F.content_type.in_([CT.PHOTO]), ProfileEdit.photos)
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

    master: Master = await MasterDAO.get_master_by_tg_id(message.from_user.id,
                                                         populate=True)
    master.validated = None
    await MasterDAO.update_master(master.to_upload(), master.documentId)

    await MasterDAO.update_photos(tg_id=message.from_user.id,
                                  photos=media_group)

    text = await texts.get_text_from_strapi("registration_photo_success")

    await message.answer(text,
                         reply_markup=MainMenuKeyboard.show_anket_update())


@router.callback_query(F.data == "show_anket_upate")
async def show_anket(callback: CallbackQuery, state: FSMContext):
    master: Master = await MasterDAO.get_master_by_tg_id(callback.from_user.id)
    logger.debug(master)

    text = await texts.anket_text(city=master.city.name,
                                  name=master.name,
                                  phone=master.phone_number,
                                  styles=master.styles_names,
                                  about=master.about_master)

    media_group = MediaGroupBuilder(caption="Портфолио")
    for photo in master.photos:
        media_group.add(type=InputMediaType.PHOTO,
                        media=URLInputFile(f"{STRAPI_MEDIA_URL}{photo['url']}",
                                           "photo_image"))

    try:
        await callback.message.answer_media_group(media_group.build(),
                                                  caption=text)

        await callback.message.answer_photo(
            URLInputFile(f"{STRAPI_MEDIA_URL}{master.profile_image['url']}",
                         "main_image"),
            caption="Фото профиля:",
            reply_markup=RegisterKeyboards.finish())

        await callback.message.answer(text=text)
    except TelegramNetworkError as e:
        logger.error(e)
        await callback.message.answer(text=text)
        await callback.message.answer(text="Отправить на проверку",
                                      reply_markup=RegisterKeyboards.finish())
    await state.set_data({"master_documentId": master.documentId})
    await state.set_state(ProfileEdit.finish)


@router.callback_query(F.data == "finish_registration", ProfileEdit.finish)
async def finish(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    documentId = data["master_documentId"]

    master: Master = await MasterDAO.get_master(documentId)

    city: CityPydantic = master.city.name

    admins = await AdminDAO.get_admins()
    admin_text = await texts.anket_to_admin(name=master.name,
                                            username=master.username,
                                            city=city,
                                            phone=master.phone_number,
                                            styles=master.styles_names,
                                            about=master.about_master,
                                            master_url=master.master_url)

    for admin in admins:

        media_group = MediaGroupBuilder(caption=admin_text)

        for photo in master.photos:
            media_group.add(type=InputMediaType.PHOTO,
                            media=URLInputFile(
                                f"{STRAPI_MEDIA_URL}{photo['url']}",
                                "photo_image"))
        try:
            await bot.send_media_group(admin, media_group.build())
            await bot.send_message(chat_id=admin, text=admin_text)
            await bot.send_photo(
                admin,
                URLInputFile(
                    f"{STRAPI_MEDIA_URL}{master.profile_image['url']}",
                    "photo_image"),
                caption="Фото профиля",
                reply_markup=RegisterKeyboards.confirm_master(
                    master.documentId, True))
        except TelegramNetworkError as e:
            await bot.send_message(
                chat_id=admin,
                text=admin_text,
                reply_markup=RegisterKeyboards.confirm_master(
                    master.documentId, True))
        await callback.message.delete()
        await callback.message.answer(
            text="Ваша заявка будет расмотренна администратором",
            reply_markup=ReplyKeyboardRemove())
        await state.clear()
