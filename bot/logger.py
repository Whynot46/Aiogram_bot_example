import logging
import os
from datetime import datetime
from functools import wraps
from aiogram import Bot
from aiogram.types import Message


# Создаем директорию для логов, если она не существует
if not os.path.exists("logs"):
    os.makedirs("logs")


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Формат сообщений
    handlers=[
        logging.FileHandler(f"logs/bot_{datetime.now().strftime('%Y-%m-%d')}.log"),  # Логирование в файл с датой
        logging.StreamHandler()  # Логирование в консоль
    ]
)


# Создаем логгер
logger = logging.getLogger(__name__)


# Декоратор для обработки ошибок
def error_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as error:
            # Логируем ошибку
            logger.error(f"{func.__name__}: {error}", exc_info=True)
            
            # Отправляем сообщение об ошибке пользователю (если есть объект Message)
            for arg in args:
                if isinstance(arg, Message):
                    bot = kwargs.get("bot") or arg.bot
                    await bot.send_message(arg.chat.id, "Произошла ошибка. Пожалуйста, попробуйте ещё раз.")
                    break
    return wrapper