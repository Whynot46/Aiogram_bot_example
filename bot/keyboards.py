from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton


async def get_reply_keyboard():
    reply_keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='reply кнопка')]
    ], resize_keyboard=True)
    return reply_keyboard


async def get_inline_keyboard():
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='inline кнопка', callback_data='inline_callback')]
            ]
    )
    return inline_keyboard
    

async def remove_keyboard():
    return ReplyKeyboardRemove()