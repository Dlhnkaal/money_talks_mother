import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook import configure_app
from aiohttp import web

from config import BOT_TOKEN  # Импорт токена из config.py

# === Настройка логирования ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Инициализация бота и диспетчера ===
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# === Машина состояний ===
class Form(StatesGroup):
    waiting_for_nickname = State()
    confirming_participation = State()

# === Обработчики команд и состояний ===
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(
        types.KeyboardButton("Участвовать в розыгрыше"),
        types.KeyboardButton("Статус участия")
    )
    kb.row(
        types.KeyboardButton("Отказаться от участия"),
        types.KeyboardButton("Помощь")
    )
    await message.answer("Привет! Чем могу помочь?", reply_markup=kb)
    await state.update_data(giveaway_id=1)


@dp.message(lambda m: m.text == "Участвовать в розыгрыше")
async def participate_start(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, введи свой никнейм для участия:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Form.waiting_for_nickname)

@dp.message(Form.waiting_for_nickname)
async def receive_nickname(message: types.Message, state: FSMContext):
    nickname = message.text.strip()
    if len(nickname) < 2:
        await message.answer("Никнейм слишком короткий, попробуй ещё раз:")
        return
    await state.update_data(nickname=nickname)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Подтвердить никнейм", "Ввести никнейм заново", "Отменить участие")
    await message.answer(f"Ты ввёл никнейм: {nickname}\nПодтверди или введи заново.", reply_markup=kb)
    await state.set_state(Form.confirming_participation)

@dp.message(Form.confirming_participation)
async def confirm_nickname(message: types.Message, state: FSMContext):
    text = message.text.strip().lower()
    data = await state.get_data()
    nickname = data.get("nickname")
    giveaway_id = data.get("giveaway_id")
    user_id = message.from_user.id

    if text == "подтвердить никнейм":
        await message.answer(f"Отлично, {nickname}! Твой ник сохранён.")
        await state.clear()

    elif text == "ввести никнейм заново":
        await message.answer("Пожалуйста, введи никнейм ещё раз:", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Form.waiting_for_nickname)

    elif text == "отменить участие":
        await message.answer("Твоё участие отменено.", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()

    else:
        await message.answer("Пожалуйста, выбери одну из кнопок: Подтвердить никнейм, Ввести никнейм заново или Отменить участие.")

@dp.message(lambda m: m.text == "Статус участия")
async def check_status(message: types.Message):
    await message.answer("Пока у тебя нет статуса участия.")

@dp.message(lambda m: m.text == "Помощь")
async def help_message(message: types.Message):
    text = (
        "Вот что я могу:\n"
        "- Участвовать в розыгрыше — начать регистрацию\n"
        "- Статус участия — проверить, оплачено ли участие\n"
        "- Отказаться от участия — удалить свои данные из розыгрыша\n\n"
        "Если есть вопросы — пиши сюда!"
    )
    await message.answer(text)

# === Основная точка входа ===
async def main():
    # Установка webhook
    app = web.Application()
    webhook_path = f"/{bot.token}"  # Путь, по которому будут приходить обновления
    configure_app(app, dp, webhook_path)

    runner = web.AppRunner(app)
    await runner.setup()

    host = "0.0.0.0"
    port = int(os.getenv("PORT", "8080"))  # Render использует PORT=10000 или другой динамический

    site = web.TCPSite(runner, host, port)
    logger.info(f"✅ Web server started on port {port}")

    webhook_url = f"https://money_talks_mother.onrender.com{webhook_path}" 
    await bot.set_webhook(webhook_url)

    await site.start()
    await asyncio.Event().wait()  # Держим сервер активным


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
