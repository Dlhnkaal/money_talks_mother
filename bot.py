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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("🚀 Бот успешно запущен!")

async def health_check(request):
    return web.Response(text="🏓 Pong")

async def on_startup(bot: Bot):
    webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
    await bot.set_webhook(webhook_url)
    logger.info(f"✅ Вебхук установлен: {webhook_url}")

async def start_webhook():
    app = web.Application()
    app.router.add_get("/ping", health_check)
    
    # Правильная регистрация обработчика вебхука
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )
    webhook_requests_handler.register(app, path="/webhook")
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()

    logger.info(f"🤖 Сервер запущен на порту {PORT}")
    await asyncio.Event().wait()

async def start_polling():
    await bot.delete_webhook()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        # Пытаемся запустить вебхук, при ошибке переключаемся на polling
        asyncio.run(start_webhook())
    except Exception as e:
        logger.error(f"❌ Ошибка вебхука: {e}")
        logger.info("🔄 Переключаемся на polling режим...")
        asyncio.run(start_polling())
