from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from config import BOT_TOKEN, CHANNEL_USERNAME
from payment import create_payment

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот для розыгрышей 🚀")

@dp.message(Command("create_giveaway"))
async def cmd_create_giveaway(message: types.Message):
    await message.answer("Пока создаём вручную (в следующем шаге добавим форму).")

@dp.message(Command("post_giveaway"))
async def cmd_post_giveaway(message: types.Message):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Участвовать", callback_data="join_giveaway")]
    ])
    await bot.send_message(chat_id=CHANNEL_USERNAME, text="🎁 Новый розыгрыш! Жми 'Участвовать' 👇", reply_markup=kb)

@dp.callback_query(lambda c: c.data == "join_giveaway")
async def process_join(call: types.CallbackQuery):
    amount = 500  # тестовая сумма
    payment = create_payment(amount, call.from_user.id)
    url = payment.confirmation.confirmation_url
    await bot.send_message(chat_id=call.from_user.id, text=f"Оплати участие: {url}")

    await call.answer()

# Запуск
if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))
