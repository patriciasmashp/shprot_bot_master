import asyncio

from loguru import logger
from service.BaseApi.StrapiApi import StrapiApi
from config import TOKEN
from arq import create_pool
from aiogram import Bot


# from scheduller.config import config
# Here you can configure the Redis connection.
# The default is to connect to localhost:6379, no password.
async def check_inst_media_container(ctx, user_id, text):
    logger.debug("123")
    


async def send_message(ctx, user_id, text):
    exec_bot: Bot = ctx['bot']
    await exec_bot.send_message(user_id, text)


async def startup(ctx):
    ctx['bot'] = Bot(TOKEN)


async def shutdown(ctx):
    exec_bot: Bot = ctx['bot']
    await exec_bot.close()
