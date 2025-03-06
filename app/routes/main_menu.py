from aiogram import F, Router
from aiogram.types import (Message, CallbackQuery)
from aiogram.fsm.context import FSMContext

from service.DAO.AdminDAO import AdminDAO
from service import texts
from service.keyboards.MainMenuKeyboard import MainMenuKeyboard
from utils.states.Register import Register
from service.schemas.Master import Master
from service.DAO.MasterDAO import MasterDAO
from create_bot import bot

router = Router(name="menu")


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
    
    await message.answer(text=text)
    
@router.message(F.text == "Сообщение разработчикам")
async def contact_developers(message: Message):
    text = await texts.get_text_from_strapi("contact_developers")
    url = await AdminDAO.get_tech_url()
    kb = MainMenuKeyboard.tech_link(url)
    await message.answer(text=text, reply_markup=kb)