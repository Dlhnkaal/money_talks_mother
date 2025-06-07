import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web
from config import BOT_TOKEN, PORT, RENDER_EXTERNAL_URL

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("🤖 Бот работает! Отправьте /help для списка команд")

async def index(request):
    return web.Response(text="Добро пожаловать в бота!")

async def ping(request):
    return web.Response(text="pong")

async def setup_webhook():
    webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
    try:
        await bot.delete_webhook()
        await bot.set_webhook(webhook_url)
        logger.info(f"Webhook установлен: {webhook_url}")
        return True
    except Exception as e:
        logger.error(f"Ошибка вебхука: {e}")
        return False

async def start_server():
    app = web.Application()
    
    # Регистрация маршрутов
    app.router.add_get("/", index)
    app.router.add_get("/ping", ping)
    
    # Настройка вебхука Telegram
    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=BOT_TOKEN.split(':')[1]  # Используем часть токена как секрет
    )
    webhook_handler.register(app, path="/webhook")
    
    # Запуск сервера
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()

    logger.info(f"Сервер запущен на порту {PORT}")
    
    if await setup_webhook():
        logger.info("Бот запущен в режиме вебхука")
    else:
        logger.warning("Запускаю в режиме polling...")
        await dp.start_polling(bot)
    
    await asyncio.Event().wait()  # Бесконечное ожидание

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except Exception as e:
        logger.critical(f"Фатальная ошибка: {e}")
        exit(1)
