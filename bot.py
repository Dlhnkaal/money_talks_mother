import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
from config import BOT_TOKEN  # Импорт токена из config.py
import os


logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class Form(StatesGroup):
    waiting_for_nickname = State()
    confirming_participation = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Участвовать в розыгрыше", "Статус участия", "Отказаться от участия", "Помощь")
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

async def run_bot():
    polling_task = asyncio.create_task(dp.start_polling(bot))

    async def handle(request):
        return web.Response(text="Bot is running!")

    app = web.Application()
    app.router.add_get("/", handle)

    port = int(os.getenv("PORT", "10000"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    logging.info(f"✅ Web server started on port {port}")

    await polling_task

if __name__ == "__main__":
    asyncio.run(run_bot())
