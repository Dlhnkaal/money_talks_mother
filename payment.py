from yookassa import Payment
from yookassa import Configuration
from config import SHOP_ID, SHOP_SECRET_KEY

Configuration.account_id = SHOP_ID
Configuration.secret_key = SHOP_SECRET_KEY

def create_payment(amount, user_id):
    payment = Payment.create({
        "amount": {
            "value": f"{amount}.00",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/forpaidlottery_bot"
        },
        "capture": True,
        "description": f"Lottery payment by user {user_id}"
    })

    return payment
