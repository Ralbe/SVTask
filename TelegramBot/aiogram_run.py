import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram import BaseMiddleware
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import asyncio
from utils.stateform import NewAds, CheckMessage, ViewingAds, ProfileStates, Profile
from DataBase.UserDB import (
    add_category, get_ads, insert_new_ad, get_category_id, get_location_id, close_connection,
    get_user_id_by_tg_id, set_user_data, get_user_data, get_categories, get_saved_by_user,
    remove_ad_from_saved, add_ad_in_saved, add_location
)
from keyboards.keyboards import (
    main_kb, ads_kb_if_saved, ads_kb_if_not_saved, confirm_kb, red_kb, back_kb, filter_kb,
    set_user_data_kb, ads_ikb
)
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
# from dotenv import load_dotenv
import os

# Load environment variables
# load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN") or '7588331682:AAHWaQdhjofYczgtFvFj3-EPYBzxR6dCKUY'  # Fallback for testing

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

# Данные о полях профиля
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

@dp.message(Command("start"))
async def handle_menu_command(message: Message, state: FSMContext):
    await state.clear()
    try:
        get_user_id_by_tg_id(message.from_user.id)  # Ensure user exists in DB
        data = get_user_data(message.from_user.id)
        await state.update_data({
            "first_name": data[0][0],
            "second_name": data[0][1],
            "phone": data[0][2],
            "email": data[0][3]
        })
        await enter_profile_mode(message, state)
    except Exception as e:
        logging.error(f"Error in start command: {e}")
        await message.answer("Произошла ошибка. Попробуйте снова.")

@dp.message(F.text == "🏠На главную")
async def handle_main_text(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите желаемый раздел.", reply_markup=main_kb)

#######################################################################
# Profile Management

@dp.message(F.text == "👤Профиль")
async def profile_command(message: Message, state: FSMContext):
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

@dp.message(F.text.in_(PROFILE_FIELDS.keys()))
async def select_profile_field(message: Message, state: FSMContext):
    """Обработчик выбора поля профиля для редактирования"""
    field_info = PROFILE_FIELDS[message.text]
    
    await state.set_state(ProfileStates.waiting_for_field)
    await state.update_data(
        editing_field=field_info["field_name"],
        field_config=message.text  # Сохраняем ключ конфига
    )
    
    reply_markup = field_info.get("keyboard", lambda: ReplyKeyboardRemove())()
    await message.answer(field_info["prompt"], reply_markup=reply_markup)

@dp.message(ProfileStates.waiting_for_field, F.content_type.in_({"text", "contact"}))
async def process_profile_field(message: Message, state: FSMContext):
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

@dp.message(F.text == "✅Сохранить профиль")
async def save_profile_handler(message: Message, state: FSMContext):
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

@dp.message(F.text == "❌Сбросить профиль")
async def reset_profile_handler(message: Message, state: FSMContext):
    """Сброс данных профиля"""
    await state.set_data({})
    await message.answer("Данные профиля сброшены", reply_markup=set_user_data_kb)

async def enter_profile_mode(message: Message, state: FSMContext):
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

#######################################################################
# Ad Browsing and Filtering

@dp.message(F.text == "🕶Объявления")
async def show_ads(message: Message, state: FSMContext):
    await state.update_data(
        viewing_ad=0,
        author='не указан',
        only_saved=False,
        saved_ads=get_saved_by_user(get_user_id_by_tg_id(message.from_user.id))
    )
    await state.set_state(ViewingAds.viewing_ad)
    await display_current_ad(message, state)

async def check_ad_filters(ad: tuple, filters: dict, state: FSMContext) -> bool:
    ad_id, ad_author, _, _, ad_category, ad_city, ad_price = ad
    data = await state.get_data()
    liked_list = data.get("saved_ads", [])
    only_saved = data.get("only_saved", False)

    if only_saved and (ad_id,) not in liked_list:
        return False
    if filters['author'] != 'не указан' and ad_author != filters['author']:
        return False
    if filters['category'] != 'не указана' and ad_category != filters['category']:
        return False
    if filters['city'] != 'не указан' and ad_city != filters['city']:
        return False
    if filters['price_min'] != 'не указана' and ad_price < int(filters['price_min']):
        return False
    if filters['price_max'] != 'не указана' and ad_price > int(filters['price_max']):
        return False
    return True

async def find_next_filtered_ad(current_index: int, filters: dict, state: FSMContext, forward: bool = True) -> int:
    ads = get_ads()
    if not ads:
        return -1
    step = 1 if forward else -1
    checked = 0
    total_ads = len(ads)
    while checked < total_ads:
        current_index = (current_index + step) % total_ads
        if current_index < 0:
            current_index = total_ads - 1
        if await check_ad_filters(ads[current_index], filters, state):
            return current_index
        checked += 1
    return current_index

async def display_current_ad(message: Message, state: FSMContext):
    try:
        ads = get_ads()
    except Exception as e:
        logging.error(f"Failed to fetch ads: {e}")
        await message.answer("Ошибка при загрузке объявлений.")
        return

    data = await state.get_data()
    current_index = data.get("viewing_ad", 0)
    filters = {
        'category': data.get('category', 'не указана'),
        'city': data.get('city', 'не указан'),
        'price_min': data.get('price_min', 'не указана'),
        'price_max': data.get('price_max', 'не указана'),
        'author': data.get('author', 'не указан')
    }

    if not ads:
        await message.answer("Нет доступных объявлений.")
        return

    if not await check_ad_filters(ads[current_index], filters, state):
        current_index = await find_next_filtered_ad(current_index, filters, state, forward=True)
        await state.update_data(viewing_ad=current_index)

    ad = ads[current_index]
    liked = (ad[0],) in data.get("saved_ads", [])

    ad_text = (
        f"<b>Категория</b>: {ad[4]}\n"
        f"<b>Местоположение</b>: {ad[5]}\n"
        f"<b>Заголовок</b>: {ad[2]}\n"
        f"<b>Описание</b>: {ad[3]}\n"
        f"<b>Цена</b>: {ad[6]}₽"
    )
    await message.answer(ad_text, reply_markup=ads_kb_if_saved if liked else ads_kb_if_not_saved)
    logging.info(f"Displayed ad {current_index}/{len(ads)} with filters: {filters}")

@dp.message(F.text == "Вперед➡️", ViewingAds.viewing_ad)
async def next_ad(message: Message, state: FSMContext):
    data = await state.get_data()
    current_index = data.get("viewing_ad", 0)
    filters = {
        'category': data.get('category', 'не указана'),
        'city': data.get('city', 'не указан'),
        'price_min': data.get('price_min', 'не указана'),
        'price_max': data.get('price_max', 'не указана'),
        'author': data.get('author', 'не указан')
    }
    new_index = await find_next_filtered_ad(current_index, filters, state, forward=True)
    await state.update_data(viewing_ad=new_index)
    await display_current_ad(message, state)

@dp.message(F.text == "⬅️Назад", ViewingAds.viewing_ad)
async def prev_ad(message: Message, state: FSMContext):
    data = await state.get_data()
    current_index = data.get("viewing_ad", 0)
    filters = {
        'category': data.get('category', 'не указана'),
        'city': data.get('city', 'не указан'),
        'price_min': data.get('price_min', 'не указана'),
        'price_max': data.get('price_max', 'не указана'),
        'author': data.get('author', 'не указан')
    }
    new_index = await find_next_filtered_ad(current_index, filters, state, forward=False)
    await state.update_data(viewing_ad=new_index)
    await display_current_ad(message, state)

async def show_filters(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(
        f"Фильтры установлены:\n"
        f"Категория: {data.get('category', 'не указана')}\n"
        f"Город: {data.get('city', 'не указан')}\n"
        f"Цена от: {data.get('price_min', 'не указана')}\n"
        f"Цена до: {data.get('price_max', 'не указана')}",
        reply_markup=filter_kb
    )

async def enter_filter_mode(message: Message, state: FSMContext):
    await state.set_state(ViewingAds.filters)
    await show_filters(message, state)

@dp.message(F.text == "⚙️Фильтры")
async def filters_command(message: Message, state: FSMContext):
    await enter_filter_mode(message, state)

@dp.message(F.text == "📁Категория")
async def set_category(message: types.Message, state: FSMContext):
    await state.set_state(ViewingAds.category)
    await message.answer("Выберите категорию: ", reply_markup=types.ReplyKeyboardRemove())

@dp.message(ViewingAds.category)
async def process_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer(f"Категория установлена: {message.text}", reply_markup=filter_kb)
    await enter_filter_mode(message, state)

@dp.message(F.text == "🏙️Город")
async def set_city(message: types.Message, state: FSMContext):
    await state.set_state(ViewingAds.city)
    await message.answer("Введите город:", reply_markup=types.ReplyKeyboardRemove())

@dp.message(ViewingAds.city)
async def process_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer(f"Город установлен: {message.text}", reply_markup=filter_kb)
    await enter_filter_mode(message, state)

@dp.message(F.text == "💰Цена от")
async def set_price_min(message: types.Message, state: FSMContext):
    await state.set_state(ViewingAds.price_min)
    await message.answer("Введите минимальную цену:", reply_markup=types.ReplyKeyboardRemove())

@dp.message(ViewingAds.price_min)
async def process_price_min(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)
        await state.update_data(price_min=price)
        await message.answer(f"Минимальная цена установлена: {price}", reply_markup=filter_kb)
    except ValueError:
        await message.answer("Пожалуйста, введите число!")
    await enter_filter_mode(message, state)

@dp.message(F.text == "💰Цена до")
async def set_price_max(message: types.Message, state: FSMContext):
    await state.set_state(ViewingAds.price_max)
    await message.answer("Введите максимальную цену:", reply_markup=types.ReplyKeyboardRemove())

@dp.message(ViewingAds.price_max)
async def process_price_max(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)
        await state.update_data(price_max=price)
        await message.answer(f"Максимальная цена установлена: {price}", reply_markup=filter_kb)
    except ValueError:
        await message.answer("Пожалуйста, введите число!")
    await enter_filter_mode(message, state)

@dp.message(F.text == "❤️В избранном")
async def remove_from_saved(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        ads = get_ads()
        ad = ads[data["viewing_ad"]]
        remove_ad_from_saved(ad[0], get_user_id_by_tg_id(message.from_user.id))
        await state.update_data(saved_ads=get_saved_by_user(get_user_id_by_tg_id(message.from_user.id)))
        await message.answer("Объявление удалено из избранного", reply_markup=ads_kb_if_not_saved)
        await message.delete()
        await display_current_ad(message, state)
    except Exception as e:
        logging.error(f"Error removing from saved: {e}")
        await message.answer("Ошибка при удалении из избранного.")

@dp.message(F.text == "♡Добавить в избранное")
async def add_to_saved(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        ads = get_ads()
        ad = ads[data["viewing_ad"]]
        add_ad_in_saved(ad[0], get_user_id_by_tg_id(message.from_user.id))
        await state.update_data(saved_ads=get_saved_by_user(get_user_id_by_tg_id(message.from_user.id)))
        await message.answer("Объявление добавлено в избранное", reply_markup=ads_kb_if_saved)
        await message.delete()
        await display_current_ad(message, state)
    except Exception as e:
        logging.error(f"Error adding to saved: {e}")
        await message.answer("Ошибка при добавлении в избранное.")

@dp.message(F.text == "❌Сбросить фильтры")
async def finish_filters(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.set_data({
        "viewing_ad": data.get("viewing_ad", 0),
        "saved_ads": data.get("saved_ads", []),
        "only_saved": False,
        "author": "не указан"
    })
    await show_filters(message, state)

@dp.message(F.text == "Мои объявления")
async def show_own_ads(message: Message, state: FSMContext):
    await state.update_data(
        viewing_ad=0,
        saved_ads=get_saved_by_user(get_user_id_by_tg_id(message.from_user.id)),
        author=get_user_id_by_tg_id(message.from_user.id),
        only_saved=False
    )
    await state.set_state(ViewingAds.viewing_ad)
    await display_current_ad(message, state)

@dp.message(F.text == "Сохраненные объявления")
async def show_saved_ads(message: Message, state: FSMContext):
    await state.update_data(
        viewing_ad=0,
        saved_ads=get_saved_by_user(get_user_id_by_tg_id(message.from_user.id)),
        only_saved=True,
        author="не указан"
    )
    await state.set_state(ViewingAds.viewing_ad)
    await display_current_ad(message, state)

#######################################################################
# Ad Creation

@dp.message(F.text == "✔️Разместить объявление")
async def new_ads(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(NewAds.title)
    await message.reply("1) Введите название товара")

@dp.message(NewAds.title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.reply("2) Введите описание товара")
    await state.set_state(NewAds.description)

@dp.message(NewAds.description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.reply("3) Укажите категорию товара")
    await state.set_state(NewAds.category)

@dp.message(NewAds.category)
async def process_category(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.reply("4) Запишите город в формате: <b>Город</b>")
    await state.set_state(NewAds.location)

@dp.message(NewAds.location)
async def process_location(message: Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.reply("5) Укажите цену")
    await state.set_state(NewAds.money)

@dp.message(NewAds.money)
async def process_money(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        await state.update_data(money=price)
        data = await state.get_data()
        ad_text = (
            f"<b>Заголовок</b>: {data['title']}\n"
            f"<b>Описание</b>: {data['description']}\n"
            f"<b>Категория</b>: {data['category']}\n"
            f"<b>Местоположение</b>: {data['location']}\n"
            f"<b>Цена</b>: {price}₽"
        )
        await message.answer("Ваше объявление будет выглядеть так:\n\n" + ad_text, reply_markup=confirm_kb)
        await state.set_state(NewAds.confirm)
    except ValueError:
        await message.reply("Пожалуйста, введите число!")

@dp.message(NewAds.confirm)
async def message_okey(message: Message, state: FSMContext):
    if message.text == "✅Разместить":
        try:
            data = await state.get_data()
            tg_id = message.from_user.id
            category = data["category"]
            location = data["location"]
            title = data["title"]
            description = data["description"]
            money = data["money"]

            user_id = get_user_id_by_tg_id(tg_id)
            category_id = get_category_id(category)
            if not category_id:
                category_id = add_category(category)
            location_id = get_location_id(location)
            if not location_id:
                location_id = add_location(location)

            insert_new_ad(user_id, category_id, location_id, title, description, money)
            await message.reply("Ваше объявление размещено")
            await state.clear()
            await handle_menu_command(message, state)
        except Exception as e:
            logging.error(f"Error publishing ad: {e}")
            await message.answer("Ошибка при размещении объявления.")
    elif message.text == "✍️Редактировать":
        await state.set_state(NewAds.change)
        await message.answer("Какую информацию вы хотите изменить?", reply_markup=red_kb)
    else:
        data = await state.get_data()
        ad_text = (
            f"<b>Заголовок</b>: {data['title']}\n"
            f"<b>Описание</b>: {data['description']}\n"
            f"<b>Категория</b>: {data['category']}\n"
            f"<b>Местоположение</b>: {data['location']}\n"
            f"<b>Цена</b>: {data['money']}₽"
        )
        await message.answer("Ваше объявление будет выглядеть так:\n\n" + ad_text, reply_markup=confirm_kb)

@dp.message(NewAds.change)
async def select_field_to_edit(message: Message, state: FSMContext):
    field_map = {
        "Заголовок": "title",
        "Описание": "description",
        "Категория": "category",
        "Город": "location",
        "Цена": "money",
        "Назад": "back"
    }
    choice = message.text
    if choice not in field_map:
        await message.answer("Пожалуйста, выберите поле для редактирования из списка", reply_markup=red_kb)
        return

    if choice == "Назад":
        await state.set_state(NewAds.confirm)
        data = await state.get_data()
        ad_text = (
            f"<b>Заголовок</b>: {data['title']}\n"
            f"<b>Описание</b>: {data['description']}\n"
            f"<b>Категория</b>: {data['category']}\n"
            f"<b>Местоположение</b>: {data['location']}\n"
            f"<b>Цена</b>: {data['money']}₽"
        )
        await message.answer("Ваше объявление:\n\n" + ad_text, reply_markup=confirm_kb)
        return

    field_name = field_map[choice]
    await state.update_data(editing_field=field_name)
    prompts = {
        "title": "Введите новый заголовок:",
        "description": "Введите новое описание:",
        "category": "Введите новую категорию:",
        "location": "Введите новый город в формате: <b>Город</b>:",
        "money": "Введите новую цену:"
    }
    await message.answer(prompts[field_name], reply_markup=back_kb)
    await state.set_state(NewAds.editing_field)

@dp.message(NewAds.editing_field)
async def process_field_edit(message: Message, state: FSMContext):
    if message.text.lower() == "назад":
        await state.set_state(NewAds.change)
        await message.answer("Выберите поле для редактирования:", reply_markup=red_kb)
        return

    data = await state.get_data()
    field_name = data.get("editing_field")
    if not field_name:
        await message.answer("Ошибка: поле для редактирования не определено")
        await state.set_state(NewAds.change)
        return

    if field_name == "money":
        try:
            price = int(message.text)
            await state.update_data({field_name: price})
        except ValueError:
            await message.answer("Пожалуйста, введите число!")
            return
    else:
        await state.update_data({field_name: message.text})

    current_data = await state.get_data()
    if "editing_field" in current_data:
        new_data = current_data.copy()
        del new_data["editing_field"]
        await state.set_data(new_data)

    await state.set_state(NewAds.confirm)
    data = await state.get_data()
    ad_text = (
        f"<b>Заголовок</b>: {data['title']}\n"
        f"<b>Описание</b>: {data['description']}\n"
        f"<b>Категория</b>: {data['category']}\n"
        f"<b>Местоположение</b>: {data['location']}\n"
        f"<b>Цена</b>: {data['money']}₽"
    )
    await message.answer("Изменения сохранены. Ваше объявление:\n\n" + ad_text, reply_markup=confirm_kb)

# Start the bot
async def main():
    try:
        await dp.start_polling(bot)
    finally:
        close_connection()

if __name__ == '__main__':
    asyncio.run(main())