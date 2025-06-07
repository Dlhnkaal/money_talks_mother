import os

BOT_TOKEN = '7792344421:AAEcvmznP_NKvHth0-roic3fmj7IduhyPag'
CHANNEL_USERNAME = '@twelvemua'
DATABASE_URL = os.getenv("DATABASE_URL")
SHOP_ID = '1102570'
SHOP_SECRET_KEY = 'test_pOQVVRWofLkmBQfDc5H_ALXUywMM8V30BQS_ed_2xKN'

# Новые параметры для Render
RENDER_DOMAIN = "money-talks-mother.onrender.com"
PORT = int(os.getenv("PORT", "10000"))  # Render использует порт 10000
