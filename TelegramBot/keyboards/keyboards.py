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
        [KeyboardButton(text="✔️Разместить объявление"),
        KeyboardButton(text="⚙️Фильтры")],
        [KeyboardButton(text="🏠На главную")]], resize_keyboard=True,
    input_field_placeholder="Воспользуйтесь меню:"
)

back_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Назад")]], resize_keyboard=True,
    input_field_placeholder="Воспользуйтесь меню:"
)

confirm_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅Разместить")],
        [KeyboardButton(text="✍️Редактировать")]], 
          resize_keyboard=True,
          input_field_placeholder="Воспользуйтесь меню:"
)

# confirm_kb = ReplyKeyboardMarkup(
#     keyboard=[
#         [KeyboardButton(text="Разместить✅")],
#         [KeyboardButton(text="Редактировать✍️")],
#         [KeyboardButton(text="✔️Разместить объявление")],
#         [KeyboardButton(text="name"),
#          KeyboardButton(text="opisanie"),
#          KeyboardButton(text="cat"),
#          KeyboardButton(text="1"),
#          KeyboardButton(text="999")]], resize_keyboard=True,
#     input_field_placeholder="Воспользуйтесь меню:"
# )

filter_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔎Содержит"),
            KeyboardButton(text="✅Сохранить фильтры")
        ],
        [
            KeyboardButton(text="📂Категория"),
            KeyboardButton(text="🏙️Город")
        ],
        [
            KeyboardButton(text="Цена от"),
            KeyboardButton(text="Цена до")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Воспользуйтесь меню:"
)

red_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Заголовок"),
         KeyboardButton(text="Описание")],
        [KeyboardButton(text="Категория"),
         KeyboardButton(text="Город"),
         KeyboardButton(text="Цена")]
    ], resize_keyboard=True,
    input_field_placeholder="Воспользуйтесь меню:"
    )

reg_kb = ReplyKeyboardMarkup(
    keyboard=[
        # Первый ряд - одна кнопка "Имя"
        [KeyboardButton(text='Имя')],
        
        # Второй ряд - одна кнопка "Фамилия"
        [KeyboardButton(text='Фамилия')],
        
        # Третий ряд - одна кнопка "Номер телефона"
        [KeyboardButton(text='Номер телефона')],
        
        # Четвертый ряд - одна кнопка "Почта"
        [KeyboardButton(text='Почта')],
        
        # Пятый ряд - одна кнопка "Сохранить данные"
        [KeyboardButton(text="Сохранить данные")]
    ],
    resize_keyboard=True, 
    one_time_keyboard=True,
    input_field_placeholder="Воспользуйтесь меню:"
)