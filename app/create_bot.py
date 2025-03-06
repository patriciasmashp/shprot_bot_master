from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from config import TOKEN

bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

