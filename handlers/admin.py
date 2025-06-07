from aiogram import Dispatcher, types
from aiogram.filters import Command
import db
from config import ADMIN_USERNAME, CHANNEL_USERNAME

# ACTIVE_RAFFLE_ID — пока просто ставим 1
ACTIVE_RAFFLE_ID = 1

def register_handlers(dp: Dispatcher):
    @dp.message(Command("results"))
    async def show_results(message: types.Message):
        if message.from_user.username != ADMIN_USERNAME:
            await message.answer("У вас нет доступа к этой команде.")
            return
        
        participants = await db.get_paid_participants(ACTIVE_RAFFLE_ID)
        if not participants:
            await message.answer("Нет оплаченных участниц.")
            return

        winner = participants[0]  # можно сделать random.choice(participants)
        text = f"🎉 Победительница розыгрыша: @{winner} 🎉"

        # Отправляем в канал
        await message.bot.send_message(f"@{CHANNEL_USERNAME}", text)

        await message.answer("Результаты опубликованы в канале!")
