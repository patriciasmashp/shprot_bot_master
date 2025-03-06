from typing import Type
from loguru import logger
from service.DAO.BaseDAO import BaseDAO
from config import PAGES_SIZE
from service.keyboards import PaginateKeyboard
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from utils.pagination.PaginationData import PaginateAct, PaginateCallback


class Paginator():

    def __init__(
            self,
            dao,
            field: str,  # Имя поля, которое нужно отобразить
            curent=None,
            num_entries=None,
            max_pages=None,
            keyboard: PaginateKeyboard = PaginateKeyboard) -> None:
        if curent:
            self.current = curent
        else:
            self.current = 1
        self.offset = (self.current - 1) * PAGES_SIZE
        self.limit = PAGES_SIZE,
        max_pages = max_pages,
        self.num_entries = num_entries
        self.dao: Type[BaseDAO] = dao
        self.selected = None
        self.field = field
        self.keyboard: Type[PaginateKeyboard] = keyboard

    async def get(self):

        enities, page_data = await self.dao.paginate(page=self.current)
        self.max_page = page_data['pageCount']
        return enities

    async def process_select(self, query: CallbackQuery,
                             callback_data: PaginateCallback):
        
        if callback_data.act == PaginateAct.next:
            logger.debug(callback_data.act)
            paginator = Paginator(
                dao=self.dao,
                field=self.field,
                curent=callback_data.current + 1,
                num_entries=self.num_entries,
            )
            enyties = await paginator.get()

            _kb = self.keyboard.get(enyties, self.field, callback_data.current + 1,
                                    paginator.max_page)
            kb = InlineKeyboardMarkup(inline_keyboard=_kb)
            await query.message.edit_reply_markup(reply_markup=kb)
            # await state.set_state(AdminStatesGroup.UsersControll.users_lsit)

        if callback_data.act == PaginateAct.prev:
            paginator = Paginator(
                dao=self.dao,
                field=self.field,
                curent=callback_data.current - 1,
                num_entries=self.num_entries,
            )
            enyties = await paginator.get()
            _kb = self.keyboard.get(enyties, self.field,
                                    callback_data.current - 1,
                                    paginator.max_page)
            kb = InlineKeyboardMarkup(inline_keyboard=_kb)
            await query.message.edit_reply_markup(reply_markup=kb)
            # await state.set_state(AdminStatesGroup.UsersControll.users_lsit)

        if callback_data.act == PaginateAct.set:
            await query.message.delete_reply_markup()
            await query.message.delete()
            return callback_data.set_id

    async def get_kb(self, entities=None):
        if entities is None:
            entities = await self.get()
        kb = self.keyboard.get(entities, self.field, self.current, self.max_page)

        return InlineKeyboardMarkup(inline_keyboard=kb)
