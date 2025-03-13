import asyncio
from typing import Any, Awaitable, Callable, Union

from loguru import logger
from service import texts
from service.schemas.Master import Master
from service.DAO.MasterDAO import MasterDAO
from aiogram import BaseMiddleware
from create_bot import bot
from aiogram.types.message import Message
from aiogram.types.update import Update


class AlbumMiddleware(BaseMiddleware):
    album_data: dict = {}

    def __init__(self, latency: Union[int, float] = 0.01):
        self.latency = latency

    async def __call__(self, handler: Callable[[Message, dict[str, Any]],
                                               Awaitable[Any]],
                       message: Message, data: dict[str, Any]) -> Any:
        if not message.media_group_id:
            await handler(message, data)
            return
        try:
            self.album_data[message.media_group_id].append(message)
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)

            data['_is_last'] = True
            data["album"] = self.album_data[message.media_group_id]
            await handler(message, data)

        if message.media_group_id and data.get("_is_last"):
            del self.album_data[message.media_group_id]
            del data['_is_last']


class AuthMiddleware(BaseMiddleware):

    async def __call__(self, handler: Callable[[Message, dict[str, Any]],
                                               Awaitable[Any]],
                       message: Message, data: dict[str, Any]) -> Any:
        if message is not None:
            master_id = message.from_user.id

        master: Master = await MasterDAO.get_master_by_tg_id(master_id)

        if master is None:

            return

        await handler(message, data)


#         if message.text == "Редактировать анкету":
#             await handler(message, data)
#             return

#         # Если анкета еще на проерке
#         if master.validated is None:
#             await handler(message, data)
#             return

#         text = await texts.get_text_from_strapi("welcome_msg_not_confirmed")

#         await bot.send_message(master_id, text)
#         return
