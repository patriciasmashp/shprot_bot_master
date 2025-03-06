from io import BytesIO
from aiogram import F, Router
from aiogram.types import (Message, CallbackQuery)
from aiogram.fsm.context import FSMContext
from loguru import logger
from aiogram.exceptions import TelegramBadRequest
from service.BaseApi.InstagramAPI import InstagramAPI
from service.BaseApi.S3 import S3
from utils.utils import bufered_photo
from service.BaseApi.VkApi import VkApi
from service import texts
from utils.states.Register import Register
from service.schemas.Master import Master
from service.DAO.MasterDAO import MasterDAO
from create_bot import bot
from filetype import guess as guess_type

router = Router(name="confirmation")


@router.callback_query(F.data.startswith("confirm_master"))
async def confirm_master(callback: CallbackQuery, state: FSMContext):
    is_update, document_id, confirm = callback.data.split("|")
    update = is_update.split(":")[1] == "update"

    master: Master = await MasterDAO.get_master(document_id)
    if master is None:
        await callback.message.answer(
            text="Пользователь отклонен другим администратором")
        return

    if master.validated and not update:
        await callback.message.answer(
            text="Пользователь уже подтвержден другим администратором")
        return

    if confirm == "yes":
        master.validated = True
        await MasterDAO.update_master(master, master.documentId)
        await callback.message.answer(text=f"{master.name} успешно подтвержден"
                                      )

        text = await texts.get_text_from_strapi(
            "registration_master_success_alert")
        await bot.send_message(master.master_id, text=text)

    else:
        try:
            await callback.message.edit_caption(
                caption="Напишите причину отказа")
        except TelegramBadRequest as e:
            await callback.message.answer("Напишите причину отказа")
        await state.set_state(Register.reason_refusal)
        await state.set_data({"master": master, "update": update})


@router.message(Register.reason_refusal)
async def reason_refusal(message: Message, state: FSMContext):
    reason = message.text
    data = await state.get_data()
    master: Master = data["master"]
    await state.clear()
    await bot.send_message(master.master_id,
                           f"Ваш профиль отклонен:\n{reason}")

    if data["update"]:
        master.validated = False
        await MasterDAO.update_master(master, master.documentId)
        return
    await MasterDAO.delete_master(master.documentId)
    await message.answer("Регистрация мастера отклонена")


@router.callback_query(F.data.startswith("post|"))
async def moderate_post(callback: CallbackQuery, state: FSMContext):
    _, acepted, document_id, media_ids, social = callback.data.split("|")
    acepted = acepted == "y"
    media_ids = media_ids.split(',')
    media = []
    media_urls = []

    for media_id in media_ids:
        media_bytes = S3.get_object(media_id)
        media_type = guess_type(media_bytes).MIME.split('/')[0]
        media.append(media_bytes)
        media_urls.append(f"https://s3.timeweb.cloud/35761e62-846cee9c-4299-4891-8e39-fc2d6f5b2938/{media_id}")

    if acepted:
        await MasterDAO.aqure_bonuses(document_id)
        logger.debug(social)
        if social == "ig":

            if media_type == 'image':

                await InstagramAPI.post_photo(message=callback.message.text,
                                              images=media_urls)
            else:
                await InstagramAPI.post_video(message=callback.message.text,
                                              video=media_urls[0])
        else:
            if media_type == 'image':

                await VkApi.post_photo(message=callback.message.text, images=media)
            else:
                await VkApi.post_video(message=callback.message.text,
                                    video=media[0])

    await callback.message.answer(
        text="Пост успешно проверен" if acepted else "Пост отклонен")
