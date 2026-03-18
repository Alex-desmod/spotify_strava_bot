import asyncio
import os
import logging
import uvicorn

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from bot_strava.handlers import common_handlers, watcher_handlers, calc_handlers
from bot_strava.services.promocatcher import PromoWatcher
from web_server.server import app
from bot_strava.database import init_db


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# async def run_web_server():
#     """Function to run the FastAPI web-server."""
#     config = uvicorn.Config(app, host="127.0.0.1", port=8000)
#     server = uvicorn.Server(config)
#     await server.serve()


async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    watcher = PromoWatcher(bot, int(ADMIN_CHAT_ID))
    dp = Dispatcher()
    dp.workflow_data["watcher"] = watcher
    dp.workflow_data["admin_id"] = int(ADMIN_CHAT_ID)
    dp.include_routers(
        watcher_handlers.router,
        calc_handlers.router,
        common_handlers.router
    )
    await init_db()
    # asyncio.create_task(run_web_server())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        datefmt="%Y-%m-%d %H:%M:%S",
                        format="[%(asctime)s.%(msecs)03d] %(module)s %(levelname)s: %(message)s")
    logger = logging.getLogger(__name__)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("The bot is off")