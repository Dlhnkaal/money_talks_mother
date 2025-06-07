import logging
import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiohttp import web
from config import BOT_TOKEN, PORT, RENDER_EXTERNAL_URL

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Проверка токена перед запуском
def validate_token(token: str) -> bool:
    if not token or token.count(':') != 1:
        return False
    bot_id, bot_key = token.split(':')
    return bot_id.isdigit() and len(bot_key) >= 30

if not validate_token(BOT_TOKEN):
    logger.critical("❌ Invalid BOT_TOKEN format!")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer("Bot is working!")

async def health_check(request):
    return web.Response(text="✅ Bot is healthy")

async def setup_webhook():
    webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
    try:
        await bot.delete_webhook()
        await bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")
        return True
    except Exception as e:
        logger.error(f"Webhook setup failed: {e}")
        return False

async def start_bot():
    app = web.Application()
    app.router.add_get("/health", health_check)
    app.router.add_post("/webhook", dp._setup_webhook_app(bot))
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    if not await setup_webhook():
        logger.error("Falling back to polling...")
        await dp.start_polling(bot)
    else:
        logger.info("Bot started in webhook mode")
        await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except Exception as e:
        logger.critical(f"Bot crashed: {e}")
        exit(1)
