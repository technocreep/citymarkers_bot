from aiogram.types.reply_keyboard import ReplyKeyboardMarkup, KeyboardButton


def start_help_keyboard():
    return ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text='start')], [KeyboardButton(text='help')]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
        )
