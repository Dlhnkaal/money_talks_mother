from aiogram import Dispatcher, types
from aiogram.filters import CommandStart
import db
from config import PAY_URL

# Допустим, пока активный розыгрыш всегда raffle_id = 1
ACTIVE_RAFFLE_ID = 1

def register_handlers(dp: Dispatcher):
    @dp.message(CommandStart(deep_link=True))
    async def start_raffle(message: types.Message, command: CommandStart.CommandObject):
        if command.args == "raffle123":
            await db.add_participant(message.from_user.username, ACTIVE_RAFFLE_ID)
            await message.answer(
                "Привет, очень рада, что ты решила поучаствовать. Желаю тебе удачи! ✨",
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text="💳 Оплатить", url=PAY_URL)]
                ])
            )
