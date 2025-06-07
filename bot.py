import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, Update
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# === Настройка логирования ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Загрузка токена из config.py или замени на свой ===
from config import BOT_TOKEN

# === Инициализация бота и диспетчера ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# === Простой обработчик команды /start ===
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Бот работает через Webhook!")

# === Telegram Request Handler ===
class MyWebhookRequestHandler(SimpleRequestHandler):
    async def handle(self, request: web.Request):
        update = await request.json()
        telegram_update = Update(**update)
        await self.dispatcher.feed_update(bot=self.bot, update=telegram_update)
        return web.Response(text="OK")

# === Тестовый эндпоинт для проверки работы сервера ===
async def ping(request):
    return web.Response(text="Pong!")

# === Основная точка входа ===
async def main():
    # 1. Создаем веб-приложение
    app = web.Application()

    # 2. Добавляем тестовый маршрут ДО setup_application
    app.router.add_get("/ping", ping)

    # 3. Регистрируем диспетчер
    setup_application(app, dp, bot=bot)

    webhook_path = f"/{bot.token}"
    logger.info(f"Webhook path: {webhook_path}")

    # 4. Регистрируем хендлер для приёма обновлений от Telegram
    MyWebhookRequestHandler(bot=bot, dispatcher=dp).register(app, path=webhook_path)

    runner = web.AppRunner(app)
    await runner.setup()

    host = "0.0.0.0"
    port = int(os.getenv("PORT", "8080"))

    site = web.TCPSite(runner, host, port)
    logger.info(f"✅ Web server started on port {port}")

    webhook_url = f"https://money_talks_mother.onrender.com{webhook_path}"    
    logger.info(f"Setting webhook to {webhook_url}")
    await bot.set_webhook(webhook_url)
    logger.info("✅ Webhook set successfully")

    await site.start()
    await asyncio.Event().wait()  # Держим сервер активным


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
