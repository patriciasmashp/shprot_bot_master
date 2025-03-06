
import asyncio
import logging
from middleware import AlbumMiddleware
from create_bot import bot, dp
from utils.utils import register_routers

# Генерация таблиц
# asyncio.run(generate_tables(engine))

# Загрузка данных
# asyncio.run(load_data())
async def main():

    register_routers()
    dp.message.middleware(AlbumMiddleware())
    # dp.message.middleware(AuthMiddleware())
    await dp.start_polling(bot)


if __name__ == "__main__":
    console_out = logging.StreamHandler()
    file_handler = logging.FileHandler("./logs/logs.log", encoding="utf8")
    formatter = logging.Formatter("\n%(asctime)s - %(levelname)s\n%(message)s")
    file_handler.setFormatter(formatter)
    logging.basicConfig(handlers=(file_handler, console_out),
                        level=logging.INFO)
    asyncio.run(main())
