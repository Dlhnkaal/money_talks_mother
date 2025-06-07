import os

# Важно: используйте os.getenv() для безопасности
BOT_TOKEN = os.environ['BOT_TOKEN']  # Обязательно через переменные окружения
CHANNEL_USERNAME = '@twelvemua'
DATABASE_URL = os.getenv("DATABASE_URL")
SHOP_ID = '1102570'
SHOP_SECRET_KEY = 'test_pOQVVRWofLkmBQfDc5H_ALXUywMM8V30BQS_ed_2xKN'

# Настройки для Render
RENDER_EXTERNAL_URL = os.environ['RENDER_EXTERNAL_URL']  # Автоматически задаётся Render
PORT = int(os.environ.get("PORT", "10000"))
