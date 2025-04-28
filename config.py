import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получение переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", 0))  # Преобразуем в int

# Для отладки
if not BOT_TOKEN:
    print("Ошибка: Не найден токен бота в переменных окружения")
if ADMIN_CHAT_ID == 0:
    print("Предупреждение: ADMIN_CHAT_ID не установлен, уведомления администратору не будут отправляться")
