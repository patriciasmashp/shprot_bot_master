from typing import List, Type
from aiogram.types import InlineKeyboardButton
from loguru import logger
from service.schemas.StrapiBase import StrapiBase
from utils.pagination.PaginationData import PaginateCallback, PaginateAct


class PaginateKeyboard():

    def get(
        enitities: List[Type[StrapiBase]],
        field: str,  # Имя поля, которое нужно отобразить
        page=1,
        max_page=1,
    ) -> list:
        inline_kb = []

        chunk_size = 2
        enity_chunks = [enitities[i:i + chunk_size] for i in range(0, len(enitities), chunk_size)]
        
        for enity_chunk in enity_chunks:
            row = []
            for enityModel in enity_chunk:
                enity = enityModel.model_dump()      
                row.append(
                    InlineKeyboardButton(
                        text=str(enity[field]),
                        callback_data=PaginateCallback(act=PaginateAct.set,
                                                    set_id=enity["documentId"]).pack())
                )
            inline_kb.append(row)

        if max_page != 1:
            if page == max_page:
                inline_kb.append([
                    InlineKeyboardButton(text="⬅️ Предыдущие",
                                         callback_data=PaginateCallback(
                                             act=PaginateAct.prev,
                                             current=page).pack()),
                    InlineKeyboardButton(text=f"{page}/{max_page}",
                                         callback_data="_"),
                ])
            elif page == 1:
                inline_kb.append([
                    InlineKeyboardButton(text=f"{page}/{max_page}",
                                         callback_data="_"),
                    InlineKeyboardButton(text="Следующие ➡️",
                                         callback_data=PaginateCallback(
                                             act=PaginateAct.next,
                                             current=page,
                                         ).pack()),
                ])
            else:
                inline_kb.append([
                    InlineKeyboardButton(text="←",
                                         callback_data=PaginateCallback(
                                             act=PaginateAct.prev,
                                             current=page,
                                         ).pack()),
                    InlineKeyboardButton(text=f"{page}/{max_page}",
                                         callback_data="_"),
                    InlineKeyboardButton(text="→",
                                         callback_data=PaginateCallback(
                                             act=PaginateAct.next,
                                             current=page,
                                         ).pack()),
                ], )
        return inline_kb


class ControllPaginateKeyBoard(PaginateKeyboard):

    def get(enitities, page=1, max_page=1):

        kb = PaginateKeyboard.get(enitities, page, max_page)
        kb.append([InlineKeyboardButton(text="Добавить", callback_data="add")])
        return kb
