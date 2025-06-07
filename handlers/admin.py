from aiogram import Dispatcher, types
from aiogram.filters import Command
import db
from config import ADMIN_USERNAME, CHANNEL_USERNAME
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def register_handlers(dp: Dispatcher):
    @dp.message(Command("create_raffle"))
    async def create_raffle_start(message: types.Message):
        if message.from_user.username != ADMIN_USERNAME:
            await message.answer("У вас нет доступа к этой команде.")
            return
        await message.answer("Введите максимальное количество участниц:")
        dp.fsm_data = {'step': 'max_participants'}

    @dp.message()
    async def process_admin_steps(message: types.Message):
        if message.from_user.username != ADMIN_USERNAME:
            return  # Игнорируем не-админов

        fsm = getattr(dp, 'fsm_data', {})

        if fsm.get('step') == 'max_participants':
            try:
                max_participants = int(message.text)
                dp.fsm_data = {
                    'step': 'payment_url',
                    'max_participants': max_participants
                }
                await message.answer("Введите ссылку для оплаты:")
            except ValueError:
                await message.answer("Введите число!")

        elif fsm.get('step') == 'payment_url':
            payment_url = message.text
            max_participants = dp.fsm_data['max_participants']
            raffle_id = await db.create_raffle(max_participants, payment_url)

            # Очищаем FSM
            dp.fsm_data = {}

            # Отправляем кнопку в канал
            await message.bot.send_message(
                chat_id=f"@{CHANNEL_USERNAME}",
                text=f"🎁 Новый розыгрыш №{raffle_id}! Жми кнопку ниже чтобы участвовать!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🎟 Участвую", url=f"https://t.me/{message.bot.me.username}?start=join_{raffle_id}")]
                ])
            )
            await message.answer(f"Розыгрыш №{raffle_id} создан и опубликован в канал!")
