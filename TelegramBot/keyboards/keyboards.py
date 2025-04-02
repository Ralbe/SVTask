from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🔐Авторизация')]
        ], resize_keyboard=True, one_time_keyboard=True,
    input_field_placeholder="Воспользуйтесь меню:"
)

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🕶Объявления'), KeyboardButton(text='📋Вакансии')],
        [KeyboardButton(text='Профиль'),
         KeyboardButton(text='🚪Выйти с аккаунта')]
        ], resize_keyboard=True, one_time_keyboard=True,
    input_field_placeholder="Воспользуйтесь меню:"
)


ads_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⬅️Назад", callback_data="prev_ad"),
         KeyboardButton(text="Вперед➡️", callback_data="next_ad")],
        [KeyboardButton(text="✔️Разместить объявление")],
        [KeyboardButton(text="🏠На главную")]], resize_keyboard=True,
    input_field_placeholder="Воспользуйтесь меню:"
)

confirm_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Разместить✅")],
        [KeyboardButton(text="Редактировать")]], resize_keyboard=True,
    input_field_placeholder="Воспользуйтесь меню:"
)
