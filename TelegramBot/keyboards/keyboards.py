from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder 

from DataBase.UserDB import get_categories

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🔐Авторизация')]
        ], resize_keyboard=True, one_time_keyboard=True,
    input_field_placeholder="Воспользуйтесь меню:"
)

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🕶Объявления'), KeyboardButton(text='📋Вакансии')],
        [KeyboardButton(text='👤Профиль'),
         KeyboardButton(text='🚪Выйти с аккаунта')]
        ], resize_keyboard=True, one_time_keyboard=True,
    input_field_placeholder="Воспользуйтесь меню:"
)


ads_kb_if_saved = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⬅️Назад", callback_data="prev_ad"),
         KeyboardButton(text="Вперед➡️", callback_data="next_ad")],
        [KeyboardButton(text="✔️Разместить объявление"),
        KeyboardButton(text="⚙️Фильтры")],
        [KeyboardButton(text="Мои объявления"),
        KeyboardButton(text="Сохраненные объявления")],
        [KeyboardButton(text="🏠На главную"),
         KeyboardButton(text="❤️В избранном")]], resize_keyboard=True,
    input_field_placeholder="Воспользуйтесь меню:"
)

ads_kb_if_not_saved = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⬅️Назад", callback_data="prev_ad"),
         KeyboardButton(text="Вперед➡️", callback_data="next_ad")],
        [KeyboardButton(text="✔️Разместить объявление"),
        KeyboardButton(text="⚙️Фильтры")],
        [KeyboardButton(text="Мои объявления"),
        KeyboardButton(text="Сохраненные объявления")],
        [KeyboardButton(text="🏠На главную"),
         KeyboardButton(text="♡Добавить в избранное")]], resize_keyboard=True,
    input_field_placeholder="Воспользуйтесь меню:"
)


ads_ikb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="prev_ad"),
            InlineKeyboardButton(text="Вперед ➡️", callback_data="next_ad")
        ],
        [
            InlineKeyboardButton(text="✔️ Разместить объявление", callback_data="create_ad"),
            InlineKeyboardButton(text="⚙️ Фильтры", callback_data="filters")
        ],
        [
            InlineKeyboardButton(text="🏠 На главную", callback_data="main_menu"),
            InlineKeyboardButton(text="", callback_data="main_menu")
        ]
    ]
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
            KeyboardButton(text="🕶Объявления"),
            #KeyboardButton(text="✅Сохранить фильтры"),
            KeyboardButton(text="❌Сбросить фильтры")
        ],
        [
            KeyboardButton(text="📁Категория"),
            KeyboardButton(text="🏙️Город")
        ],
        [
            KeyboardButton(text="💰Цена от"),
            KeyboardButton(text="💰Цена до")
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

# red_ikb = InlineKeyboardMarkup(InlineKeyboardButton(text="Заголовок", callback_data="Заголовок"))


set_user_data_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='👤Имя'),
        KeyboardButton(text='👥Фамилия')],
        
        # Третий ряд - одна кнопка "Номер телефона"
        [KeyboardButton(text='📧Email'),
        KeyboardButton(text='📞Телефон')],
        
        [KeyboardButton(text='🏠На главную'),
         KeyboardButton(text="✅Сохранить профиль")
        ]
    ],
    resize_keyboard=True, 
    one_time_keyboard=True,
    input_field_placeholder="Воспользуйтесь меню:"
)



# ad_ikb = InlineKeyboardMarkup(row_width = 2)
# ad_ikb.add(InlineKeyboardButton("❤️", callback_data="save_this_ad"),
#            InlineKeyboardButton("idk", callback_data="save_this_ad"))


async def category_keyboard():
    keyboard = ReplyKeyboardBuilder()
    categories = await get_categories()  # Предполагаем, что это асинхронная функция
    
    for category in categories:
        keyboard.add(KeyboardButton(text=str(category[0])))  # На всякий случай приводим к строке
    
    # Добавляем кнопки навигации в отдельный ряд
    keyboard.row(KeyboardButton(text="⬅️"), KeyboardButton(text="➡️"))
    
    # Настраиваем раскладку (например, по 2 кнопки в ряду для категорий)
    keyboard.adjust(2, repeat=True)
    
    return keyboard.as_markup()