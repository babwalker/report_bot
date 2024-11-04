from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

def meny_keyboard():
    keyboard = [
        [KeyboardButton(text="Materials")]    
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def cancel():
    keyboard = [
        [KeyboardButton(text="Cancel")]    
    ]

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def materials_keyboard():
    inline_keyboard = [
        [InlineKeyboardButton(text="Proxy", callback_data="proxy")],
        [InlineKeyboardButton(text="Sessions", callback_data="sessions"),
        InlineKeyboardButton(text="View loaded session", callback_data="loaded_session")]
    ]
    inline_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return inline_markup
