from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


main_kb = ReplyKeyboardMarkup(
keyboard = [
    [KeyboardButton(text='Объявления'),KeyboardButton(text='Вакансии')],
    [KeyboardButton(text='Профиль'),KeyboardButton(text='🚪Выйти с аккаунта')]
   ], resize_keyboard=True, one_time_keyboard=True,
        input_field_placeholder="Воспользуйтесь меню:"
)