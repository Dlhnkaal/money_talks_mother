from aiogram import Dispatcher, types
from aiogram.filters import CommandStart
import db

def register_handlers(dp: Dispatcher):
    @dp.message(CommandStart(deep_link=True))
    async def start_raffle(message: types.Message):
        args = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        if args and args.startswith("join_"):
            raffle_id = int(args.split("_")[1])
            raffle = await db.get_raffle(raffle_id)
            if not raffle or not raffle['active']:
                await message.answer("Розыгрыш не найден или завершён.")
                return

            if raffle['current_participants'] >= raffle['max_participants']:
                await message.answer("Набор на этот розыгрыш завершён.")
                return

            await db.add_participant(message.from_user.username, raffle_id)
            await message.answer(
                f"Привет, ты участвуешь в розыгрыше №{raffle_id}! 🎉",
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text="💳 Оплатить", url=raffle['payment_url'])]
                ])
            )
