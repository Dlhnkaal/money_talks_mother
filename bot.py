import logging
import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, Update
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web
from config import BOT_TOKEN, RENDER_DOMAIN, PORT

# === Настройка логирования ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

# === Тестовые эндпоинты ===
async def index(request):
    return web.Response(text="🤖 Bot is running! Use /ping to test.")

async def ping(request):
    return web.Response(text="🏓 Pong!")

async def handle_404(request):
    return web.Response(text="🚫 Not Found", status=404)

async def main():
    # 1. Создаем веб-приложение
    app = web.Application()
    
    # 2. Регистрируем маршруты
    app.router.add_get("/", index)
    app.router.add_get("/ping", ping)
    
    # 3. Формируем путь для вебхука (используем только секретную часть токена)
    secret_path = BOT_TOKEN.split(':')[1]  # Берем часть после ':'
    webhook_path = f"/{secret_path}"
    logger.info(f"Webhook path: {webhook_path}")

    # 4. Регистрируем хендлер для вебхука
    MyWebhookRequestHandler(bot=bot, dispatcher=dp).register(app, path=webhook_path)
    
    # 5. Обработчик для 404 ошибок
    app.router.add_route("*", "/{tail:.*}", handle_404)

    # 6. Настраиваем и запускаем сервер
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"✅ Web server started on port {PORT}")

    # 7. Устанавливаем вебхук
    webhook_url = f"https://{RENDER_DOMAIN}{webhook_path}"
    logger.info(f"Setting webhook to {webhook_url}")
    
    try:
        await bot.set_webhook(webhook_url)
        logger.info("✅ Webhook set successfully")
    except Exception as e:
        logger.error(f"❌ Failed to set webhook: {e}")
        raise

    # 8. Держим приложение активным
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
