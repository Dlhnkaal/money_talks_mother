import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web
from config import BOT_TOKEN, PORT, RENDER_EXTERNAL_URL

SECRET_TOKEN = BOT_TOKEN.split(':')[1]  # Вынеси в переменную

async def setup_webhook():
    webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
    try:
        await bot.delete_webhook()
        await bot.set_webhook(webhook_url, secret_token=SECRET_TOKEN)  # добавь secret_token!!!
        logger.info(f"Webhook установлен: {webhook_url}")
    except Exception as e:
        logger.error(f"Ошибка вебхука: {e}")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Меню кнопок
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📋 Помощь", callback_data="help")],
    [InlineKeyboardButton(text="ℹ️ О боте", callback_data="about")]
])

# Хэндлер на /start с кнопками
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=main_menu)

# Хэндлер для обработки нажатий на кнопки
@dp.callback_query()
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data
    if data == "help":
        await callback_query.message.answer("Список команд:\n/start — запустить бота\n/help — список команд")
    elif data == "about":
        await callback_query.message.answer("Этот бот сделан на aiogram + Render 🚀")
    
    await callback_query.answer()  # чтобы убрать "часики" на кнопке

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer("Список команд:\n/start — запустить бота\n/help — список команд")

@dp.message(Command("about"))
async def about_cmd(message: types.Message):
    await message.answer("Этот бот сделан на aiogram + Render 🚀")


async def index(request):
    return web.Response(text="Добро пожаловать в бота!")

async def ping(request):
    return web.Response(text="pong")

async def start_server():
    app = web.Application()

    # Регистрация маршрутов
    app.router.add_get("/", index)
    app.router.add_get("/ping", ping)

    # Настройка webhook handler
    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=SECRET_TOKEN)
    webhook_handler.register(app, path="/webhook")

    # Запуск aiohttp сервера
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()

    logger.info(f"Сервер запущен на порту {PORT}")

    # Установка вебхука
    await setup_webhook()

    # Просто держим процесс "живым"
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except Exception as e:
        logger.critical(f"Фатальная ошибка: {e}")
        exit(1)
