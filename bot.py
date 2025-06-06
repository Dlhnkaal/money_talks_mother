from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from config import BOT_TOKEN, CHANNEL_USERNAME
from payment import create_payment
from aiohttp import web
import os
import asyncpg

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class Form(StatesGroup):
    waiting_for_nickname = State()
    confirming_participation = State()

async def get_participation_status(user_id: int, giveaway_id: int):
    conn = await asyncpg.connect(dsn=os.getenv("DATABASE_URL"))
    row = await conn.fetchrow(
        "SELECT paid FROM participants WHERE user_id = $1 AND giveaway_id = $2",
        user_id, giveaway_id
    )
    await conn.close()
    if row is None:
        return None
    return row["paid"]

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    giveaway_id = 1  # можно сделать динамически
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Участвовать в розыгрыше", "Статус участия", "Отказаться от участия", "Помощь")
    await message.answer("Привет! Чем могу помочь?", reply_markup=kb)
    await state.update_data(giveaway_id=giveaway_id)

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
        # Создаём или обновляем запись в БД
        conn = await asyncpg.connect(dsn=os.getenv("DATABASE_URL"))
        exists = await conn.fetchval(
            "SELECT COUNT(*) FROM participants WHERE user_id = $1 AND giveaway_id = $2",
            user_id, giveaway_id
        )
        if exists == 0:
            await conn.execute(
                "INSERT INTO participants (user_id, giveaway_id, paid, nickname) VALUES ($1, $2, $3, $4)",
                user_id, giveaway_id, False, nickname
            )
        else:
            await conn.execute(
                "UPDATE participants SET nickname = $1 WHERE user_id = $2 AND giveaway_id = $3",
                nickname, user_id, giveaway_id
            )
        await conn.close()

        amount = 500
        payment = create_payment(amount, user_id, metadata={"nickname": nickname, "giveaway_id": str(giveaway_id)})
        url = payment.confirmation.confirmation_url

        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("Оплатить участие", url=url))

        await message.answer(f"Отлично, {nickname}! Чтобы подтвердить участие, оплати {amount} руб:", reply_markup=kb)
        await state.clear()

    elif text == "ввести никнейм заново":
        await message.answer("Пожалуйста, введи никнейм ещё раз:", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Form.waiting_for_nickname)

    elif text == "отменить участие":
        conn = await asyncpg.connect(dsn=os.getenv("DATABASE_URL"))
        await conn.execute(
            "DELETE FROM participants WHERE user_id = $1 AND giveaway_id = $2",
            user_id, giveaway_id
        )
        await conn.close()
        await message.answer("Твоё участие отменено. Если передумаешь, всегда можешь написать мне снова.", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()

    else:
        await message.answer("Пожалуйста, выбери одну из кнопок: Подтвердить никнейм, Ввести никнейм заново или Отменить участие.")

@dp.message(lambda m: m.text == "Статус участия")
async def check_status(message: types.Message, state: FSMContext):
    data = await state.get_data()
    giveaway_id = data.get("giveaway_id") or 1
    user_id = message.from_user.id
    paid = await get_participation_status(user_id, giveaway_id)

    if paid is None:
        await message.answer("Ты пока не зарегистрирован(а) на розыгрыш. Нажми 'Участвовать в розыгрыше', чтобы начать.")
    elif paid:
        await message.answer("Ты успешно оплатил(а) участие и участвуешь в розыгрыше. Удачи!")
    else:
        await message.answer("Ты зарегистрирован(а), но ещё не оплатил(а) участие. Оплати, чтобы подтвердить.")

@dp.message(lambda m: m.text == "Помощь")
async def help_message(message: types.Message):
    text = (
        "Вот что я могу:\n"
        "- Участвовать в розыгрыше — начать регистрацию\n"
        "- Статус участия — проверить, оплачено ли участие\n"
        "- Отказаться от участия — удалить свои данные из розыгрыша\n\n"
        "Если у тебя вопросы — пиши сюда!"
    )
    await message.answer(text)

async def start_bot():
    asyncio.create_task(dp.start_polling(bot))

    async def handle(request):
        return web.Response(text="Bot is running!")

    app = web.Application()
    app.router.add_get("/", handle)

    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print(f"✅ Web server started on port {port}")

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(start_bot())

