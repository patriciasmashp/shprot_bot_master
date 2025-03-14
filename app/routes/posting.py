from datetime import datetime
from random import Random
from aiogram import F, Router
from aiogram.types import (Message, CallbackQuery, ContentType as CT,
                           BufferedInputFile)
from aiogram.fsm.context import FSMContext
from loguru import logger
from aiogram.enums.parse_mode import ParseMode
from service.BaseApi.S3 import S3
from service.keyboards import SystemKeyboards
from service.DAO.AdminDAO import AdminDAO
from utils.states.PostingsStates import Posting
from utils.utils import bufered_photo, resize_image
from service import texts
from service.keyboards import PostingKeyboard, Keyboard
from utils.states.Register import Register
from service.schemas.Master import Master
from service.DAO.MasterDAO import MasterDAO
from create_bot import bot
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.enums import InputMediaType
from filetype import guess as guess_type

router = Router(name="menu")


@router.callback_query(F.data == "help", Posting.type_of_post)
async def help(callback: CallbackQuery, state: FSMContext):
    text = await texts.get_text_from_strapi("post_help")
    kb = PostingKeyboard.after_help()
    await state.clear()
    await callback.message.edit_text(text, reply_markup=kb)


@router.callback_query(F.data != "help", Posting.type_of_post)
async def select_post_type(callback: CallbackQuery, state: FSMContext):
    post_type = callback.data
    master: Master = await MasterDAO.get_master_by_tg_id(callback.from_user.id)
    
    if master is None:
        return
    
    match post_type:
        case "sketch":
            text = await texts.get_text_from_strapi("post_sketch_first")
        case "photo":
            text = await texts.get_text_from_strapi("post_photo_first")
        case "video":
            text = await texts.get_text_from_strapi("post_video_first")
            text = "Пока в разработке"
            await callback.message.edit_text(text)
            return
    await state.set_data({"post_type": post_type})
    await state.set_state(Posting.files_upload)
    await callback.message.edit_text(text)


@router.message(F.content_type.in_([CT.PHOTO, CT.VIDEO]), Posting.files_upload)
async def post_files(message: Message,
                     state: FSMContext,
                     album: list[Message] | None = None):
    data = await state.get_data()
    post_type = data.get("post_type")

    if message.video and post_type == "video":

        if 15 < message.video.duration < 60:
            buffered_video = await bufered_photo(message.video.file_id)
            text = await texts.get_text_from_strapi("post_price")
            await message.answer(text)
            await state.set_state(Posting.price)
            await state.update_data({"video": [buffered_video.read()]})
        else:
            text = await texts.get_text_from_strapi("post_error_video_duration"
                                                    )
            await message.answer(text)
        return

    if album is None and post_type in ["photo", "sketch"]:
        if message.video:
            
            await message.answer("Необходимо отправить изображения, а не видео")
            return
        buffered_photo = await bufered_photo(message.photo[-1].file_id)
        resized_image = resize_image(buffered_photo, (1080, 1350))

        await state.update_data({"photos": [resized_image.read()]})

        text = await texts.get_text_from_strapi("post_price")
        await message.answer(text)
        await state.set_state(Posting.price)
        return

    media_group = []
    if album and post_type in ["photo", "sketch"]:
        for msg in album:
            obj_dict = msg.model_dump()
            file_id = obj_dict[msg.content_type][-1]['file_id']

            buffered_photo = await bufered_photo(file_id)
            resized_image = resize_image(buffered_photo, (1080, 1350))

            media_group.append(resized_image.read())

    if len(media_group) > 3:
        text = await texts.get_text_from_strapi("posting_error_max_photo")
        return

    await state.update_data({"photos": media_group})
    text = await texts.get_text_from_strapi("post_price")
    await message.answer(text)
    await state.set_state(Posting.price)


@router.message(Posting.price)
async def post_price(message: Message, state: FSMContext):
    if message.text is None:
        return
    
    price = message.text
    await state.update_data({"price": price})

    data = await state.get_data()
    post_type = data.get("post_type")

    match post_type:
        case "sketch":
            text = await texts.get_text_from_strapi("post_body_part")
            await state.set_state(Posting.body_part)
            await message.answer(text)
            return
        case "photo":
            text = await texts.get_text_from_strapi("post_sessions")
            await state.set_state(Posting.sessions)
            await message.answer(text)
            return
        case "video":
            text = await texts.get_text_from_strapi("post_sessions")
            await state.set_state(Posting.sessions)
            await message.answer(text)
            return


@router.message(Posting.sessions)
async def post_sessions(message: Message, state: FSMContext):
    if message.text is None:
        return
    time = message.text
    await state.update_data({"time": time})

    data = await state.get_data()
    post_type = data.get("post_type")

    match post_type:
        case "photo":
            text = await texts.get_text_from_strapi("post_styles")
            await state.set_state(Posting.style)
            await message.answer(text)
            return
        case "video":
            await state.set_state(Posting.social)
            text = await texts.get_text_from_strapi("post_select_social")
            await message.answer(text, reply_markup=PostingKeyboard.socials())


@router.message(Posting.style)
async def post_style(message: Message, state: FSMContext):
    if message.text is None:
        return

    style = message.text
    await state.update_data({"style": style})

    await state.set_state(Posting.social)
    text = await texts.get_text_from_strapi("post_select_social")
    await message.answer(text, reply_markup=PostingKeyboard.socials())


@router.message(Posting.body_part)
async def post_body_part(message: Message, state: FSMContext):
    if message.text is None:
        return

    body_part = message.text
    await state.update_data({"body_part": body_part})

    await state.set_state(Posting.social)
    text = await texts.get_text_from_strapi("post_select_social")
    await message.answer(text, reply_markup=PostingKeyboard.socials())


@router.callback_query(Posting.social)
async def social(callback: CallbackQuery, state: FSMContext):

    social = callback.data
    await state.update_data({"social": social})

    text = await texts.get_text_from_strapi("post_confirm")
    await state.set_state(Posting.confirm)
    await callback.message.edit_text(text)
    await callback.message.edit_reply_markup(
        reply_markup=PostingKeyboard.show_post())


@router.callback_query(Posting.confirm, F.data == "confirm")
async def show_post(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    post_type = data.get("post_type")
    master: Master = await MasterDAO.get_master_by_tg_id(callback.from_user.id)

    match post_type:
        case "sketch":
            text = await texts.post_sketch(city=master.city.name,
                                           master_name=master.name,
                                           master_url=master.master_url,
                                           body_part=data.get("body_part"),
                                           price=data.get("price"))
            media = data["photos"]
            media_type = InputMediaType.PHOTO
        case "photo":
            text = await texts.post_photo(city=master.city.name,
                                          style=data.get("style"),
                                          time=data.get("time"),
                                          master_name=master.name,
                                          master_url=master.master_url,
                                          price=data.get("price"))

            media = data["photos"]
            media_type = InputMediaType.PHOTO
        case "video":
            text = await texts.post_video(city=master.city.name,
                                          time=data.get("time"),
                                          master_name=master.name,
                                          master_url=master.master_url,
                                          price=data.get("price"))
            media = data["video"]
            media_type = InputMediaType.VIDEO

    media_group = MediaGroupBuilder()
    await state.update_data({"text": text})
    await state.update_data({"media_type": media_type})
    await state.update_data({"media": media})
    for photo in media:
        media_group.add(type=media_type,
                        media=BufferedInputFile(photo, "photo_image"))

    await callback.message.answer_media_group(media_group.build())
    await callback.message.answer(text, reply_markup=PostingKeyboard.confirm())


@router.callback_query(Posting.confirm, F.data == "send")
async def send_post(callback: CallbackQuery, state: FSMContext):
    admins = await AdminDAO.get_admins()
    master: Master = await MasterDAO.get_master_by_tg_id(callback.from_user.id)
    data = await state.get_data()
    admin_text = f"Новый пост в {data['social']} "
    admin_text += data.get("text")
    for admin in admins:

        media_group = MediaGroupBuilder()

        media_names = []
        for index, photo in enumerate(data["media"]):
            r = Random()
            filename = f"{r.randint(a=0, b=999)}{index}.{guess_type(photo).EXTENSION}"

            media_group.add(type=data["media_type"],
                            media=BufferedInputFile(photo, filename))

            S3.upload_object(photo, filename)
            media_names.append(filename)
        await bot.send_media_group(admin, media_group.build())

        await bot.send_message(
            admin,
            admin_text,
            #    parse_mode=ParseMode.MARKDOWN,
            reply_markup=PostingKeyboard.y_n_kb(master.documentId,
                                                media_names, data['social']))
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("Пост отправлен на проверку")


@router.callback_query(Posting.confirm, F.data == "restart")
async def restart_post(callback: CallbackQuery, state: FSMContext):
    text = await texts.get_text_from_strapi("post_start")
    await state.clear()
    await state.set_state(Posting.type_of_post)
    await callback.message.answer(text,
                                  reply_markup=PostingKeyboard.type_of_post())
