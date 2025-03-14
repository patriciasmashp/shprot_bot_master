from aiogram import F, Router
from aiogram.types import (Message, CallbackQuery)
from aiogram.fsm.context import FSMContext
from aiogram import flags
from service.DAO.AdminDAO import AdminDAO
from service import texts
from service.keyboards.MainMenuKeyboard import MainMenuKeyboard
from middleware import AuthMiddleware
from service.keyboards.PostingKeyboard import PostingKeyboard
from utils.states.PostingsStates import Posting
from utils.states.Register import Register
from service.schemas.Master import Master
from service.DAO.MasterDAO import MasterDAO

router = Router(name="menu")
router.message.middleware(AuthMiddleware())


@router.message(F.text == "Редактировать анкету")
async def edit_profile(message: Message):
    master: Master = await MasterDAO.get_master_by_tg_id(message.from_user.id)
    kb = MainMenuKeyboard.edit_profile()
    text = await texts.get_text_from_strapi("edit_main")
    await message.answer(text=text, reply_markup=kb)

    if not master.validated:
        text = await texts.get_text_from_strapi("welcome_msg_not_confirmed")

        await message.answer(text)


@router.message(F.text == "Статистика профиля")
async def profile_stats(message: Message):
    master: Master = await MasterDAO.get_master_by_tg_id(message.from_user.id)
    text = "Ваша статистика:\n"
    text += f"Лайки: {master.likes}\n"
    text = "В разработке"
    await message.answer(text=text)


@router.message(F.text == "Сообщение разработчикам")
async def contact_developers(message: Message):
    text = await texts.get_text_from_strapi("contact_developers")
    url = await AdminDAO.get_tech_url()
    kb = MainMenuKeyboard.tech_link(url)
    await message.answer(text=text, reply_markup=kb)


@router.message(F.text == "Баланс")
async def balance(message: Message):
    master: Master = await MasterDAO.get_master_by_tg_id(message.from_user.id)
    text = f"Ваш баланс: {master.balance}"

    await message.answer(text=text)


@router.message(F.text == "Опубликовать пост")
async def post_start(message: Message, state: FSMContext):
    text = await texts.get_text_from_strapi("post_start")
    await state.set_state(Posting.type_of_post)
    await message.answer(text, reply_markup=PostingKeyboard.type_of_post())


@router.callback_query(F.data == "start_post")
async def post_start_cb(callback: CallbackQuery, state: FSMContext):
    text = await texts.get_text_from_strapi("post_start")
    await state.set_state(Posting.type_of_post)
    await callback.message.edit_text(
        text, reply_markup=PostingKeyboard.type_of_post())
