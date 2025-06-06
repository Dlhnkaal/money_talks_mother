from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from config import BOT_TOKEN, CHANNEL_USERNAME, DATABASE_URL
from payment import create_payment
from aiohttp import web
import os
import asyncpg

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# === START ===
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    payload = message.text.split(" ", 1)[1] if " " in message.text else None

    if payload and payload.startswith("giveaway_"):
        giveaway_id = int(payload.split("_")[1])
        
        # === Создаём платёж ===
        amount = 500
        payment = create_payment(amount, message.from_user.id)
        url = payment.confirmation.confirmation_url

        # === Добавляем участника в participants (если ещё не был добавлен) ===
        conn = await asyncpg.connect(DATABASE_URL)
        
        exists = await conn.fetchval(
            "SELECT COUNT(*) FROM participants WHERE user_id = $1 AND giveaway_id = $2",
            message.from_user.id, giveaway_id
        )

        if exists == 0:
            await conn.execute(
                "INSERT INTO participants (user_id, giveaway_id, paid) VALUES ($1, $2, $3)",
                message.from_user.id, giveaway_id, False
            )
            await message.answer("✅ Вы записаны на участие в розыгрыше!")
        else:
            await message.answer("⚠️ Вы уже записаны в этот розыгрыш.")

        await conn.close()

        # === Отправляем ссылку на оплату ===
        await message.answer(f"Для участия оплатите {amount} руб:\n{url}")

    else:
        await message.answer("Привет! Я бот для розыгрышей 🚀")

# === /create_giveaway ===
@dp.message(Command("create_giveaway"))
async def cmd_create_giveaway(message: types.Message):
    await message.answer("Пока создаём вручную (в следующем шаге добавим форму).")

# === /post_giveaway ===
@dp.message(Command("post_giveaway"))
async def cmd_post_giveaway(message: types.Message):
    giveaway_id = 1  # пока вручную (можно будет автоинкремент)
    
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(
            text="Участвовать",
            url=f"https://t.me/{(await bot.me()).username}?start=giveaway_{giveaway_id}"
        )]
    ])

    sent_message = await bot.send_message(
        chat_id=CHANNEL_USERNAME,
        text="🎁 Новый розыгрыш!\nУчаствуют: 0 человек",
        reply_markup=kb
    )

    # === Сохраняем message_id ===
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        INSERT INTO giveaways (giveaway_id, message_id, participants_count)
        VALUES ($1, $2, $3)
        ON CONFLICT (giveaway_id) DO UPDATE SET message_id = $2
    """, giveaway_id, sent_message.message_id, 0)
    await conn.close()

# === Webhook для ЮKassa ===
async def handle_payment_webhook(request):
    data = await request.json()
    print("=== Webhook получен ===", data)

    if data["event"] == "payment.succeeded":
        # Тут у тебя в payment.metadata должно быть giveaway_id и user_id
        giveaway_id = int(data["object"]["metadata"]["giveaway_id"])
        user_id = int(data["object"]["metadata"]["user_id"])

        conn = await asyncpg.connect(DATABASE_URL)

        # Обновляем участника
        await conn.execute("""
            UPDATE participants
            SET paid = TRUE
            WHERE user_id = $1 AND giveaway_id = $2
        """, user_id, giveaway_id)

        # Обновляем счётчик участников
        count = await conn.fetchval("""
            SELECT COUNT(*) FROM participants
            WHERE giveaway_id = $1 AND paid = TRUE
        """, giveaway_id)

        # Получаем message_id
        message_id = await conn.fetchval("""
            SELECT message_id FROM giveaways WHERE giveaway_id = $1
        """, giveaway_id)

        await conn.execute("""
            UPDATE giveaways SET participants_count = $1 WHERE giveaway_id = $2
        """, count, giveaway_id)

        await conn.close()

        # Редактируем сообщение в канале
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(
                text="Участвовать",
                url=f"https://t.me/{(await bot.me()).username}?start=giveaway_{giveaway_id}"
            )]
        ])

        await bot.edit_message_text(
            chat_id=CHANNEL_USERNAME,
            message_id=message_id,
            text=f"🎁 Новый розыгрыш!\nУчаствуют: {count} человек",
            reply_markup=kb
        )

        # Шлём пользователю
        await bot.send_message(chat_id=user_id, text="✅ Оплата получена! Вы участвуете в розыгрыше!")

    return web.Response(status=200)

# === Запуск ===
async def start_bot():
    asyncio.create_task(dp.start_polling(bot))

    # Веб-сервер
    app = web.Application()
    app.router.add_get("/", lambda request: web.Response(text="Bot is running!"))
    app.router.add_post("/yookassa_webhook", handle_payment_webhook)

    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print(f"✅ Web server started on port {port}")

    while True:
        await asyncio.sleep(3600)

# Запуск
if __name__ == "__main__":
    asyncio.run(start_bot())
