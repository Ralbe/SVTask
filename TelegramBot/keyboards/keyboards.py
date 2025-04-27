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

def ads_ikb(saved, your_ad):
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="prev_ad"),
                InlineKeyboardButton(text="Вперед ➡️", callback_data="next_ad")
            ],
            [InlineKeyboardButton(text="❤️В избранном" if saved else "♡Добавить в избранное",
                                  callback_data="remove_from_saved" if saved else "add_in_saved")],


            [InlineKeyboardButton(text="✏️Редактировать" if your_ad else "📱Связаться",
                                  callback_data="change_ad" if your_ad else "get_contact")]
        ]
    )
    return keyboard

# ads_ikb = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [
#             InlineKeyboardButton(text="⬅️ Назад", callback_data="prev_ad"),
#             InlineKeyboardButton(text="Вперед ➡️", callback_data="next_ad")
#         ]
#     ]
# )

ads_kb_showed = ReplyKeyboardMarkup(
    keyboard=[
        # [KeyboardButton(text="⬅️Назад", callback_data="prev_ad"),
        #  KeyboardButton(text="Вперед➡️", callback_data="next_ad")],
        [KeyboardButton(text="✔️Разместить объявление"),
        KeyboardButton(text="⚙️Фильтры")],
        [KeyboardButton(text="Мои объявления"),
        KeyboardButton(text="Сохраненные объявления")],
        [KeyboardButton(text="🏠На главную"),
         KeyboardButton(text="⬇️Скрыть меню")]], resize_keyboard=True,
    input_field_placeholder="Воспользуйтесь меню:"
)

ads_kb_hided = ReplyKeyboardMarkup(
    keyboard=[
         [KeyboardButton(text="⬆️Показать меню")]
         ], resize_keyboard=True,
    input_field_placeholder="Воспользуйтесь меню:"
)

# ads_kb_hided = ReplyKeyboardMarkup(
#     keyboard=[
#         # [KeyboardButton(text="⬅️Назад", callback_data="prev_ad"),
#         #  KeyboardButton(text="Вперед➡️", callback_data="next_ad")],
#         [KeyboardButton(text="✔️Разместить объявление"),
#         KeyboardButton(text="⚙️Фильтры")],
#         [KeyboardButton(text="Мои объявления"),
#         KeyboardButton(text="Сохраненные объявления")],
#         [KeyboardButton(text="🏠На главную"),
#          KeyboardButton(text="⬇️Скрыть меню")]], resize_keyboard=True,
#     input_field_placeholder="Воспользуйтесь меню:"
# )




back_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌Назад")]], resize_keyboard=True,
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
            # KeyboardButton(text="🏙️Город")
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
        #  KeyboardButton(text="Город"),
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


async def category_kb(categories):
    keyboard = ReplyKeyboardBuilder()

    for category in categories:
        keyboard.add(KeyboardButton(text=category[0]))
        # print(category[0] if hasattr(category, '__getitem__') else category)
    keyboard.add(KeyboardButton(text="❌Назад"))
    return keyboard.adjust(2).as_markup(resize_keyboard=True,  # Подгоняет размер кнопок
                                        one_time_keyboard=True,  # Скрывает клавиатуру после выбора
                                        input_field_placeholder="Выберите категорию")


# async def ad:
#     keyboard = ReplyKeyboardBuilder()
#     categories = await get_categories()  # Предполагаем, что это асинхронная функция
    
#     for category in categories:
#         keyboard.add(KeyboardButton(text=str(category[0])))  # На всякий случай приводим к строке
    
#     # Добавляем кнопки навигации в отдельный ряд
#     keyboard.row(KeyboardButton(text="⬅️"), KeyboardButton(text="➡️"))
    
#     # Настраиваем раскладку (например, по 2 кнопки в ряду для категорий)
#     keyboard.adjust(2, repeat=True)
    
#     return keyboard.as_markup()