import asyncio
import os
import logging
import uvicorn

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from bot_strava.handlers import router
from web_server.server import app
from bot_strava.database import init_db

# sys.path.append(os.path.dirname(os.path.abspath(os.path.join(__file__, "..", ".."))))


async def run_web_server():
    """Function to run the FastAPI web-server."""
    config = uvicorn.Config(app, host="127.0.0.1", port=8000)
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    load_dotenv()
    TOKEN = os.getenv('BOT_TOKEN')

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    await init_db()
    asyncio.create_task(run_web_server())
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        datefmt="%Y-%m-%d %H:%M:%S",
                        format="[%(asctime)s.%(msecs)03d] %(module)s %(levelname)s: %(message)s")
    logger = logging.getLogger(__name__)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning('The bot is off')