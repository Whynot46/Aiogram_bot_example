from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove


async def get_reply_keyboard():
    reply_keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='reply кнопка')]
    ], resize_keyboard=True)
    return reply_keyboard


async def remove_keyboard():
    return ReplyKeyboardRemove()