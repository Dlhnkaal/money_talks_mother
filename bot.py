import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web
from config import BOT_TOKEN, PORT, RENDER_EXTERNAL_URL
import db
import handlers.user
import handlers.admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Регистрируем хэндлеры
handlers.user.register_handlers(dp)
handlers.admin.register_handlers(dp)

async def setup_webhook():
    webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
    await bot.delete_webhook()
    await bot.set_webhook(webhook_url)
    logger.info(f"Webhook установлен: {webhook_url}")

async def start_server():
    app = web.Application()

    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=BOT_TOKEN.split(':')[1])
    webhook_handler.register(app, path="/webhook")

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()

    logger.info(f"Сервер запущен на порту {PORT}")

    await setup_webhook()

    # Инициализация БД
    await db.init_db()

    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except Exception as e:
        logger.critical(f"Фатальная ошибка: {e}")
