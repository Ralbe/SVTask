from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from DataBase.UserDB import get_user_data, set_user_data
from keyboards.keyboards import set_user_data_kb, main_kb
import logging
from utils.states import ProfileStates

PROFILE_FIELDS = {
    "👤Имя": {
        "field_name": "first_name",
        "prompt": "Введите ваше имя:",
        "validation": lambda x: (True, x) if x.strip() else (False, "Имя не может быть пустым")
    },
    "👥Фамилия": {
        "field_name": "second_name",
        "prompt": "Введите вашу фамилию:",
        "validation": lambda x: (True, x)
    },
    "📧Email": {
        "field_name": "email",
        "prompt": "Введите ваш email:",
        "validation": lambda x: (
            (True, x) if "@" in x and "." in x.split("@")[-1] 
            else (False, "Некорректный email. Попробуйте еще раз.")
        )
    },
    "📞Телефон": {
        "field_name": "phone",
        "prompt": "Введите ваш телефон или нажмите кнопку 'Поделиться контактом':",
        "keyboard": lambda: ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Поделиться контактом", request_contact=True)]],
            resize_keyboard=True
        ),
        "validation": lambda x: (
            (True, x) if x.replace("+", "").isdigit() 
            else (False, "Некорректный номер телефона. Попробуйте еще раз.")
        ),
        "process_contact": lambda contact: contact.phone_number
    }
}

async def profile_command(message: types.Message, state: FSMContext):
    """Обработчик входа в режим профиля"""
    try:
        # Загружаем данные пользователя из БД
        db_data = get_user_data(message.from_user.id)
        
        if not db_data or not db_data[0]:
            await message.answer("Профиль не найден. Давайте создадим его!")
            # Устанавливаем пустые значения
            await state.update_data({
                "first_name": "",
                "second_name": "",
                "phone": "",
                "email": ""
            })
        else:
            # Обновляем состояние данными из БД
            await state.update_data({
                "first_name": db_data[0][0] or "",
                "second_name": db_data[0][1] or "",
                "phone": db_data[0][2] or "",
                "email": db_data[0][3] or ""
            })
        
        # Входим в режим просмотра профиля
        await enter_profile_mode(message, state)
        
    except Exception as e:
        logging.error(f"Ошибка при загрузке профиля: {e}", exc_info=True)
        await message.answer(
            "⚠️ Произошла ошибка при загрузке профиля. Попробуйте позже.",
            reply_markup=main_kb
        )
        await state.clear()

async def select_profile_field(message: types.Message, state: FSMContext):
    """Обработчик выбора поля профиля для редактирования"""
    field_info = PROFILE_FIELDS[message.text]
    
    await state.set_state(ProfileStates.waiting_for_field)
    await state.update_data(
        editing_field=field_info["field_name"],
        field_config=message.text  # Сохраняем ключ конфига
    )
    
    reply_markup = field_info.get("keyboard", lambda: ReplyKeyboardRemove())()
    await message.answer(field_info["prompt"], reply_markup=reply_markup)

async def process_profile_field(message: types.Message, state: FSMContext):
    """Обработчик ввода значения для поля профиля"""
    user_data = await state.get_data()
    field_config_key = user_data["field_config"]
    field_info = PROFILE_FIELDS[field_config_key]
    
    # Обработка контакта (если поле phone и прислан контакт)
    if message.contact and field_info["field_name"] == "phone":
        value = field_info["process_contact"](message.contact)
    else:
        value = message.text
    
    # Валидация значения
    is_valid, validated_value_or_error = field_info["validation"](value)
    
    if not is_valid:
        await message.answer(validated_value_or_error)
        return
    
    # Обновляем данные в состоянии
    await state.update_data({
        user_data["editing_field"]: validated_value_or_error,
        "editing_field": None  # Сбрасываем редактируемое поле
    })
    
    # Возвращаем в режим профиля
    await enter_profile_mode(message, state)

async def save_profile_handler(message: types.Message, state: FSMContext):
    """Сохранение профиля в БД"""
    data = await state.get_data()
    
    try:
        set_user_data(
            first_name=data.get("first_name"),
            second_name=data.get("second_name"),
            email=data.get("email"),
            phone=data.get("phone"),
            tg_id=message.from_user.id
        )
        await message.answer("✅ Профиль успешно сохранён!", reply_markup=set_user_data_kb)
    except Exception as e:
        logging.error(f"Ошибка сохранения профиля: {e}")
        await message.answer("❌ Ошибка при сохранении профиля. Попробуйте позже.")

async def reset_profile_handler(message: types.Message, state: FSMContext):
    """Сброс данных профиля"""
    await state.set_data({})
    await message.answer("Данные профиля сброшены", reply_markup=set_user_data_kb)

async def enter_profile_mode(message: types.Message, state: FSMContext):
    """Отображение текущего состояния профиля"""
    data = await state.get_data()
    
    profile_info = (
        "⚙️ <b>Ваш профиль:</b>\n\n"
        f"👤 <b>Имя:</b> {data.get('first_name', 'не указано')}\n"
        f"👥 <b>Фамилия:</b> {data.get('second_name', 'не указано')}\n"
        f"📧 <b>Email:</b> {data.get('email', 'не указан')}\n"
        f"📞 <b>Телефон:</b> {data.get('phone', 'не указан')}\n\n"
        "Выберите поле для редактирования:"
    )
    
    await message.answer(text=profile_info, reply_markup=set_user_data_kb)
    await state.set_state(None)  # Сбрасываем состояние

def register_handlers(dp):
    dp.message.register(profile_command, F.text == "👤Профиль")
    dp.message.register(select_profile_field, F.text.in_(PROFILE_FIELDS.keys()))
    dp.message.register(process_profile_field, ProfileStates.waiting_for_field, F.content_type.in_({"text", "contact"}))
    dp.message.register(save_profile_handler, F.text == "✅Сохранить профиль")
    dp.message.register(reset_profile_handler, F.text == "❌Сбросить профиль")