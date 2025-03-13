
import asyncio
import logging
import os
from middleware import AlbumMiddleware, AuthMiddleware
from create_bot import bot, dp
from utils.utils import register_routers

# Генерация таблиц
# asyncio.run(generate_tables(engine))

# Загрузка данных
# asyncio.run(load_data())
async def main():

    register_routers()
    dp.message.middleware(AlbumMiddleware())
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    console_out = logging.StreamHandler()
    if os.path.exists("./logs") is False:
        os.mkdir("./logs")
    file_handler = logging.FileHandler("./logs/logs.log", encoding="utf8")
    formatter = logging.Formatter("\n%(asctime)s - %(levelname)s\n%(message)s")
    file_handler.setFormatter(formatter)
    logging.basicConfig(handlers=(file_handler, console_out),
                        level=logging.INFO)
    asyncio.run(main())
