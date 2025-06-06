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

# Запускаем бота в фоне
async def start_bot():
    asyncio.create_task(main())  # твоя функция main()

    # Фиктивный веб-сервер для Render
    async def handle(request):
        return web.Response(text="Bot is running!")

    app = web.Application()
    app.router.add_get("/", handle)

    port = int(os.environ.get("PORT", 10000))  # Render задаст PORT, иначе 10000
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print(f"✅ Web server started on port {port}")

    while True:
        await asyncio.sleep(3600)  # чтобы не завершался

# Запуск
if __name__ == "__main__":
    asyncio.run(start_bot())

# Запуск
if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))
