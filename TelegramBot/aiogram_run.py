import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InputMediaPhoto
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, CallbackQuery
import asyncio
from utils.stateform import NewAds, CheckMessage, ViewingAds, ProfileStates, Profile, NewVacancy, ViewingVacancies
from DataBase.UserDB import (
    add_category, get_ads, insert_new_ad, get_category_id, get_location_id, close_connection,
    get_user_id_by_tg_id, set_user_data, get_user_data, get_categories, get_saved_by_user,
    remove_ad_from_saved, add_ad_in_saved, add_location, increment_ad_views, get_statistic,
    get_contact_by_ad_id, update_ad, get_ad_by_id, get_user_ads, get_ad_photos, add_photo, delete_ad_photos,
    get_saved_vacancies, get_vacancies,increment_vacancy_views, get_vacancy_by_id, get_vacancy_statistics,
    get_user_vacancies,add_vacancy_to_saved, remove_vacancy_from_saved, insert_new_vacancy, 
    get_contact_by_user_id
)
from keyboards.keyboards import (
    main_kb, ads_kb_showed, ads_kb_hided, confirm_kb, red_kb, back_kb, filter_kb,
    set_user_data_kb, ads_ikb, category_kb, vacancy_edit_kb, vacancy_ikb, vacancy_kb_hided,
    vacancy_kb_showed
)
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from datetime import datetime
# from dotenv import load_dotenv
import os

# Load environment variables
# load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN") or '7588331682:AAHWaQdhjofYczgtFvFj3-EPYBzxR6dCKUY'  # Fallback for testing

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
categories = get_categories()
# print(categories, "@@@@@@@@@@@@@@@@@@@")
# for category in categories:
#         # keyboard.add(KeyboardButton(text=category[0]))
#         print(category[0],"\n")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

async def format_date(d: datetime) -> str:
    """Асинхронно форматирует дату в строку вида 'D месяц'."""
    # await asyncio.sleep(0.1)  # Имитация асинхронной задержки
    
    months = {
        1: "января", 2: "февраля", 3: "марта", 4: "апреля",
        5: "мая", 6: "июня", 7: "июля", 8: "августа",
        9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
    }
    return f"{d.day} {months[d.month]}"


# Данные о полях профиля
PROFILE_FIELDS = {
    "👤Имя": {
        "field_name": "firstname",
        "prompt": "Введите ваше имя:",
        "validation": lambda x: (True, x) if x.strip() else (False, "Имя не может быть пустым")
    },
    "👥Фамилия": {
        "field_name": "lastname",
        "prompt": "Введите вашу фамилию:",
        "validation": lambda x: (True, x) if x.strip() else (False, "Имя не может быть пустым")
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
        get_user_id_by_tg_id(message.from_user.id)  
        data = get_user_data(message.from_user.id)
        await state.update_data({
            "firstname": data[0][0],
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
                "firstname": "",
                "lastname": "",
                "phone": "",
                "email": ""
            })
        else:
            # Обновляем состояние данными из БД
            await state.update_data({
                "firstname": db_data[0][0] or "",
                "lastname": db_data[0][1] or "",
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
    print("\n\n\n",data.get("lastname"))
    try:
        set_user_data(
            firstname=data.get("firstname"),
            lastname=data.get("lastname"),
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
        f"👤 <b>Имя:</b> {data.get('firstname', 'не указано')}\n"
        f"👥 <b>Фамилия:</b> {data.get('lastname', 'не указано')}\n"
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
        saved_ads=get_saved_by_user(get_user_id_by_tg_id(message.from_user.id)),
        ad_msg_id =0,
        stat_msg_id = 0,
        showed_kb = True,
        user_id = get_user_id_by_tg_id(message.from_user.id)
    )

    data = await state.get_data()
    filters = {
        'category': data.get('category', 'не указана'),
        'city': data.get('city', 'не указан'),
        'price_min': data.get('price_min', 'не указана'),
        'price_max': data.get('price_max', 'не указана'),
        'author': get_user_id_by_tg_id(message.from_user.id)
    }
    new_index = await find_next_filtered_ad(0, filters, state, forward=True)
    await state.update_data(viewing_ad=new_index)
    await state.set_state(ViewingAds.viewing_ad)
    await display_current_ad(message, state)


async def check_ad_filters(ad: tuple, filters: dict, state: FSMContext) -> bool:
    ad_id, ad_author, _, _, ad_category, ad_city, ad_price, ad_create_date = ad
    data = await state.get_data()
    liked_list = data.get("saved_ads", [])
    only_saved = data.get("only_saved", False)

    if only_saved and (ad_id,) not in liked_list:
        return False
    if filters != None:
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
    print()
    try:
        ads = get_ads()
    except Exception as e:
        logging.error(f"Failed to fetch ads: {e}")
        await message.answer("Ошибка при загрузке объявлений.")
        return

    data = await state.get_data()
    current_index = data.get("viewing_ad", 0)
    ad = ads[current_index]
    ad_id = ad[0]
    await state.update_data({"ad_id":ad_id})
    # Получаем фото для объявления
    photos = get_ad_photos(ad_id)
    
    ad_text = (
        f"<b>Заголовок</b>: {ad[2]}\n"
        f"<b>Описание</b>: {ad[3]}\n"
        f"<b>Категория</b>: {ad[4]}\n"
        # f"<b>Местоположение</b>: {ad[5]}\n"
        f"<b>Цена</b>: {ad[6]}"
    )

    # Проверяем, является ли объявление пользовательским
    user_id = data.get('user_id')
    user_ads = get_user_ads(user_id) or []
    your_ad = (ad_id,) in user_ads
    
    if not your_ad:
        increment_ad_views(ad_id)

    liked_ad = (ad_id,) in data.get("saved_ads", [])
    
    stats = get_statistic(ad_id)
    if stats is None:
        stats = (0, 0)  # Значения по умолчанию
    if stats[1] == None:
        stats = (stats[0], 0)

    print("________________________")
    print(ad[0])
    print(ad[1])
    print(ad[2])
    print(ad[3])
    print(ad[4])
    print(ad[5])
    print(ad[6])
    print(ad[7])
    print(stats[0])
    print(stats[1])
    print("________________________")

    stats_text = (
        f"📊 <b>Статистика объявления</b>:\n"
        f"📅 Дата создания объявления: {await format_date(ad[7])}\n"
        f"👁 Просмотры: {stats[0]} | ❤️ Сохранения: {stats[1]}"
    )
    





    # try:
        # if photos:
        #     # Отправляем фото с подписью
        #     media = [InputMediaPhoto(media=photos[0], caption=ad_text)]
        #     # Добавляем остальные фото
        #     media.extend([InputMediaPhoto(media=photo) for photo in photos[1:]])
            
        #     # Удаляем старые сообщения если они есть
        #     if data.get("ad_msg_id"):
        #         await bot.delete_message(chat_id=message.chat.id, message_id=data.get("ad_msg_id"))
        #     if data.get("photo_group_id"):
        #         await bot.delete_message(chat_id=message.chat.id, message_id=data.get("photo_group_id"))
        #     if data.get("stat_msg_id"):
        #         await bot.delete_message(chat_id=message.chat.id, message_id=data.get("stat_msg_id"))
            
        #     # Отправляем группу фото
        #     sent_messages = await bot.send_media_group(chat_id=message.chat.id, media=media)
        #     photo_group_id = sent_messages[0].message_id
            
        #     # Отправляем статистику и кнопки
        #     stat_msg = await message.answer(stats_text, reply_markup=ads_kb_showed if data.get("showed_kb") else ads_kb_hided)
        #     buttons_msg = await message.answer("Действия:", reply_markup=ads_ikb(liked_ad, your_ad))
            
        #     await state.update_data(
        #         photo_group_id=photo_group_id,
        #         stat_msg_id=stat_msg.message_id,
        #         ad_msg_id=buttons_msg.message_id
        #     )
        # else:
        #     # Старая логика для объявлений без фото
        #     await bot.edit_message_text(text=stats_text, chat_id=message.chat.id, 
        #                               message_id=data.get("stat_msg_id"),
        #                               reply_markup=ads_kb_showed if data.get("showed_kb") else ads_kb_hided)
        #     await bot.edit_message_text(text=ad_text, chat_id=message.chat.id, 
        #                               message_id=data.get("ad_msg_id"),
        #                               reply_markup=ads_ikb(liked_ad, your_ad))
    # except Exception as e:
        # logging.error(f"Failed to change ad text: {e}")
        # Удаляем старые сообщения если они есть
    if data.get("ad_msg_id"):
        await bot.delete_message(chat_id=message.chat.id, message_id=data.get("ad_msg_id"))
    if data.get("stat_msg_id"):
        await bot.delete_message(chat_id=message.chat.id, message_id=data.get("stat_msg_id"))
    if data.get("photo_group_id"):
        await bot.delete_message(chat_id=message.chat.id, message_id=data.get("photo_group_id"))
    
    if photos:
        media = [InputMediaPhoto(media=photos[0], caption=ad_text)]
        media.extend([InputMediaPhoto(media=photo) for photo in photos[1:]])
        sent_messages = await bot.send_media_group(chat_id=message.chat.id, media=media)
        photo_group_id = sent_messages[0].message_id
        buttons_msg = await message.answer("Действия:", reply_markup=ads_ikb(liked_ad, your_ad))
        stat_msg = await message.answer(stats_text, reply_markup=ads_kb_showed if data.get("showed_kb") else ads_kb_hided)
        
        await state.update_data(
            photo_group_id=photo_group_id,
            stat_msg_id=stat_msg.message_id,
            ad_msg_id=buttons_msg.message_id
        )
    else:
        ad_msg = await message.answer(ad_text, reply_markup=ads_ikb(liked_ad, your_ad))    
        stat_msg = await message.answer(stats_text, reply_markup=ads_kb_showed if data.get("showed_kb") else ads_kb_hided)
        await state.update_data(
            ad_msg_id=ad_msg.message_id, 
            stat_msg_id=stat_msg.message_id,
            photo_group_id=None
        )

@dp.message(NewAds.change, F.text == "Фотографии")
async def edit_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    
    if not photos:
        text = "У этого объявления пока нет фото. Хотите добавить?"
    else:
        text = f"Сейчас прикреплено {len(photos)} фото. Что вы хотите сделать?"
    
    await message.answer(text, 
                       reply_markup=ReplyKeyboardMarkup(
                           keyboard=[
                               [KeyboardButton(text="Добавить фото"), KeyboardButton(text="Удалить все фото")],
                               [KeyboardButton(text="❌Назад")]
                           ],
                           resize_keyboard=True
                       ))
    await state.set_state(NewAds.edit_photos)

@dp.message(NewAds.edit_photos, F.text == "Добавить фото")
async def add_more_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    current_count = len(data.get("photos", []))
    remaining = 10 - current_count
    
    if remaining <= 0:
        await message.answer("Достигнут лимит в 10 фото. Удалите некоторые фото чтобы добавить новые.")
        return
    
    await message.answer(f"Пришлите до {remaining} фото. Когда закончите, нажмите 'Готово'", 
                        reply_markup=ReplyKeyboardMarkup(
                            keyboard=[[KeyboardButton(text="Готово")]],
                            resize_keyboard=True
                        ))
    await state.set_state(NewAds.add_more_photos)

@dp.message(NewAds.add_more_photos, F.photo)
async def process_additional_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    
    if len(photos) >= 10:
        await message.answer("Максимальное количество фото - 10. Нажмите 'Готово' чтобы продолжить.")
        return
    
    largest_photo = message.photo[-1]
    photos.append(largest_photo.file_id)
    
    await state.update_data(photos=photos)
    remaining = 10 - len(photos)
    await message.answer(f"Фото добавлено. Осталось {remaining} фото. Пришлите еще или нажмите 'Готово'.")

@dp.message(NewAds.add_more_photos, F.text == "Готово")
async def finish_additional_photos(message: Message, state: FSMContext):
    await show_ad_preview(message, state)

@dp.message(NewAds.edit_photos, F.text == "Удалить все фото")
async def remove_all_photos(message: Message, state: FSMContext):
    await state.update_data(photos=[])
    await message.answer("Все фото удалены.", reply_markup=red_kb)
    await state.set_state(NewAds.change)

@dp.callback_query(F.data == "next_ad")
async def next_ad(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
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
    await display_current_ad(callback.message, state)
    # await callback.message.delete()
    # await bot.delete_message(chat_id=callback.message.chat.id,
    #                     message_id=callback.message.message_id+1)
    
    # await state.update_data(ad_msg_id = callback.message.message_id, stat_msg_id = callback.message.message_id+1)

@dp.callback_query(F.data == "prev_ad")
async def prev_ad(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
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
    # await callback.message.delete()
    # await bot.delete_message(chat_id=callback.message.chat.id,
    #                     message_id=callback.message.message_id+1)

    # await state.update_data(ad_msg_id = callback.message.message_id, stat_msg_id = callback.message.message_id+1)
    await display_current_ad(callback.message, state)

@dp.callback_query(F.data == "get_contact")
async def get_contact(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    ad_id = data.get("ad_id")
    author_data = get_contact_by_ad_id(ad_id)

    # print("\n\n\n",ad_id)
    # print(author_data, "\n\n\n")
    try:
        author_name = author_data[0][0]
        author_nickname = author_data[0][1]
        author_tg_id = author_data[0][2]
        author_phone = author_data[0][3]

    except Exception as e:
        await callback.message.answer("Ошибка, попробуйте позже")

    if author_tg_id != None:
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text=f"Автор объявления: {f'[{author_nickname}({author_name})](tg://user?id={author_tg_id})'}",
            parse_mode="MarkdownV2"
            )
    else:
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text=f"Автор объявления: {author_phone} - {author_name}"
            )
    # await callback.message.answer(f"Вот ссылка на пользователя: {f'[{author_name}](tg://user?id={author_tg_id} )'}")

@dp.callback_query(F.data == "change_ad")
async def change_ad(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    ad_id = data.get("ad_id")
    ad_data = get_ad_by_id(ad_id)[0]
    
    # Получаем текущие фото объявления
    photos = get_ad_photos(ad_id)
    
    await state.update_data({
        "ad_id": ad_data[0],
        "title": ad_data[1],
        "description": ad_data[2],
        "category": ad_data[3],
        "money": ad_data[5],
        "photos": photos,  # Сохраняем текущие фото
        "changing_ad": True
    })
    
    await show_ad_preview(callback.message, state)
    await state.set_state(NewAds.confirm)

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
    await message.answer("Выберите категорию: ", reply_markup=await category_kb(categories))

@dp.message(ViewingAds.category)
async def process_category(message: types.Message, state: FSMContext):
    if message.text == "❌Назад":
        await enter_filter_mode(message, state)
    else:
        await state.update_data(category=message.text)
        await message.answer(f"Категория установлена: {message.text}", reply_markup=filter_kb)
        await enter_filter_mode(message, state)

# @dp.message(F.text == "🏙️Город")
# async def set_city(message: types.Message, state: FSMContext):
#     await state.set_state(ViewingAds.city)
#     await message.answer("Введите город:", reply_markup=types.ReplyKeyboardRemove())

# @dp.message(ViewingAds.city)
# async def process_city(message: types.Message, state: FSMContext):
#     await state.update_data(city=message.text)
#     await message.answer(f"Город установлен: {message.text}", reply_markup=filter_kb)
#     await enter_filter_mode(message, state)

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

@dp.callback_query(F.data.in_(["remove_from_saved", "add_in_saved"]))
async def handle_saved_actions(callback: CallbackQuery, state: FSMContext):
    try:
        # 1. Получаем данные
        user_id = get_user_id_by_tg_id(callback.from_user.id)
        if not user_id:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return

        data = await state.get_data()
        ad_id = data.get("ad_id")
        if not ad_id:
            await callback.answer("❌ Объявление не найдено", show_alert=True)
            return

        # 2. Выполняем действие
        if callback.data == "remove_from_saved":
            remove_ad_from_saved(ad_id, user_id)

            liked_ad = False
        else:
            add_ad_in_saved(ad_id, user_id)
            liked_ad = True

        # 3. Обновляем состояние
        try:
            saved_ads = get_saved_by_user(user_id) or []
            await state.update_data(saved_ads=saved_ads)
        except Exception as e:
            logging.error(f"Ошибка обновления состояния: {e}")

        # 4. Обновляем интерфейс
        your_ad = (ad_id,) in (get_user_ads(user_id) or [])
        try:
            stats = get_statistic((ad_id))
            data = await state.get_data()
            ad = get_ad_by_id(ad_id)
            stats_text = (
                f"📊 <b>Статистика объявления</b>:\n"
                f"📅 Дата создания объявления: {await format_date(ad[6])}\n"
                f"👁 Просмотры: {stats[0]}\n"
                f"❤️ Сохранения: {stats[1]}\n"
                # f"📞 Запросы контактов: {stats[2]}"
    )
            # await bot.edit_message_text(text = stats_text, chat_id=callback.message.chat.id, message_id = callback.message.message_id+1,
            #                             reply_markup = ads_kb_showed if data.get("showed_kb") else ads_kb_hided)
            # await bot.edit_message_reply_markup(message_id=callback.message.message_id+1, reply_markup = ads_kb_showed if data.get("showed_kb") else ads_kb_hided)
            await callback.message.edit_reply_markup(
                reply_markup=ads_ikb(liked_ad, your_ad)
            )
        except Exception as e:
            logging.error(f"Ошибка обновления интерфейса: {e}")
            # await callback.answer("✅ Обновлено")
            
        await display_current_ad(callback.message, state)

    except Exception as e:
        logging.error(f"Ошибка в обработке избранного: {e}")
        await callback.answer("❌ Ошибка при обработке запроса", show_alert=True)

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
    data = await state.get_data()
    filters = {
        'category': data.get('category', 'не указана'),
        'city': data.get('city', 'не указан'),
        'price_min': data.get('price_min', 'не указана'),
        'price_max': data.get('price_max', 'не указана'),
        'author': get_user_id_by_tg_id(message.from_user.id)
    }

    print()
    new_index = await find_next_filtered_ad(0, filters, state, forward=True)
    await state.update_data(viewing_ad=new_index)
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
    await state.update_data({"changing_ad":False})
    await message.reply("Введите название товара")

@dp.message(NewAds.title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.reply("Введите описание товара")
    await state.set_state(NewAds.description)

@dp.message(NewAds.description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.reply("Выберете категорию товара", reply_markup=await category_kb(categories))
    await state.set_state(NewAds.category)

@dp.message(NewAds.category)
async def process_category(message: Message, state: FSMContext):
    # if (message.text,) in categories:
    #     await state.update_data(category=message.text)
    #     await message.reply("4) Запишите город в формате: <b>Город</b>")
    #     await state.set_state(NewAds.location)
    if (message.text,) in categories:
        await state.update_data(category=message.text)
        await message.reply("Укажите стоимость")
        await state.set_state(NewAds.money)
    elif message.text == "❌Назад":
        await show_ads(message, state)
    else:
        await message.reply("Выберете категорию товара", reply_markup=await category_kb(categories))
        await state.set_state(NewAds.category)
    

# @dp.message(NewAds.location)
# async def process_location(message: Message, state: FSMContext):
#     await state.update_data(location=message.text)
#     await message.reply("5) Укажите цену")
#     await state.set_state(NewAds.money)

@dp.message(NewAds.money)
async def process_money(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        await state.update_data(money=price)
        await message.answer("Теперь пришлите фотографии товара (до 10 штук). Когда закончите, нажмите 'Готово'", 
                           reply_markup=ReplyKeyboardMarkup(
                               keyboard=[[KeyboardButton(text="Готово")]],
                               resize_keyboard=True
                           ))
        await state.update_data(photos=[])  # Инициализируем пустой список фото
        await state.set_state(NewAds.photos)
    except ValueError:
        await message.reply("Пожалуйста, введите число!")

@dp.message(NewAds.photos, F.photo)
async def process_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    
    if len(photos) >= 10:
        await message.answer("Максимальное количество фото - 10. Нажмите 'Готово' чтобы продолжить.")
        return
    
    # Сохраняем file_id самого большого доступного размера фото
    largest_photo = message.photo[-1]
    photos.append(largest_photo.file_id)
    
    await state.update_data(photos=photos)
    remaining = 10 - len(photos)
    await message.answer(f"Фото добавлено. Осталось {remaining} фото. Пришлите еще или нажмите 'Готово'.")

@dp.message(NewAds.photos, F.text == "Готово")
async def finish_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    
    if not photos:
        await message.answer("Вы не добавили ни одного фото.", 
                        #    reply_markup=ReplyKeyboardMarkup(
                        #        keyboard=[
                        #            [KeyboardButton(text="Да"), KeyboardButton(text="Добавить фото")]
                        #        ],
                        #        resize_keyboard=True)
                           )
        # return
    
    await show_ad_preview(message, state)

async def show_ad_preview(message: Message, state: FSMContext):
    data = await state.get_data()
    ad_text = (
        f"<b>Заголовок</b>: {data['title']}\n"
        f"<b>Описание</b>: {data['description']}\n"
        f"<b>Категория</b>: {data['category']}\n"
        f"<b>Цена</b>: {data['money']}"
    )
    
    photos = data.get("photos", [])
    
    if photos:
        # Отправляем первое фото с подписью и кнопками
        media = [InputMediaPhoto(media=photos[0], caption=ad_text)]
        # Добавляем остальные фото без подписи
        media.extend([InputMediaPhoto(media=photo) for photo in photos[1:]])
        
        await message.answer_media_group(media=media)
        await message.answer("Ваше объявление будет выглядеть так:", reply_markup=confirm_kb)
    else:
        await message.answer("Ваше объявление будет выглядеть так:\n\n" + ad_text, reply_markup=confirm_kb)
    
    await state.set_state(NewAds.confirm)

@dp.message(NewAds.confirm)
async def message_okey(message: Message, state: FSMContext):
    if message.text == "✅Разместить":
        # try:
            data = await state.get_data()
            tg_id = message.from_user.id
            category = data["category"]
            title = data["title"]
            description = data["description"]
            money = data["money"]
            photos = data.get("photos", [])

            user_id = get_user_id_by_tg_id(tg_id)
            category_id = get_category_id(category)
            if not category_id:
                category_id = add_category(category)

            if data["changing_ad"]:
                ad_id = data["ad_id"]
                update_ad(ad_id, user_id, category_id, title, description, money)
                # Удаляем старые фото
                delete_ad_photos(ad_id)
            else:
                ad_id = insert_new_ad(user_id, category_id, title, description, money)

            # Сохраняем новые фото
            for photo in photos:
                try:
                    add_photo(ad_id, photo)
                except Exception as e:
                    logging.error(f"Ошибка при сохранении фото: {e}")
                    continue

            await message.reply("✅ Ваше объявление размещено", reply_markup=main_kb)
            await state.clear()
            await handle_main_text(message, state)
        # except Exception as e:
            # logging.error(f"Error publishing ad: {e}")
            # await message.answer("❌ Ошибка при размещении объявления. Попробуйте позже.")

@dp.message(NewAds.change)
async def select_field_to_edit(message: Message, state: FSMContext):
    field_map = {
        "Заголовок": "title",
        "Описание": "description",
        "Категория": "category",
        # "Город": "location",
        "Цена": "money",
        "❌Назад": "back"
    }
    choice = message.text
    if choice not in field_map:
        await message.answer("Пожалуйста, выберите поле для редактирования из списка", reply_markup=red_kb)
        return

    if choice == "❌Назад":
        await state.set_state(NewAds.confirm)
        data = await state.get_data()
        ad_text = (
            f"<b>Заголовок</b>: {data['title']}\n"
            f"<b>Описание</b>: {data['description']}\n"
            f"<b>Категория</b>: {data['category']}\n"
            # f"<b>Местоположение</b>: {data['location']}\n"
            f"<b>Цена</b>: {data['money']}₽"
        )
        await message.answer("Ваше объявление:\n\n" + ad_text, reply_markup=confirm_kb)
        return

    field_name = field_map[choice]
    await state.update_data(editing_field=field_name)
    prompts = {
        "title": "Введите новый заголовок:",
        "description": "Введите новое описание:",
        "category": "Выберите новую категорию:",
        # "location": "Введите новый город в формате: <b>Город</b>:",
        "money": "Введите новую цену:"
    }
    await message.answer(prompts[field_name], reply_markup=back_kb if field_name != 'category' else await category_kb(categories))
    await state.set_state(NewAds.editing_field)

@dp.message(NewAds.editing_field)
async def process_field_edit(message: Message, state: FSMContext):
    if message.text.lower() == "❌Назад":
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
        # f"<b>Местоположение</b>: {data['location']}\n"
        f"<b>Цена</b>: {data['money']}"
    )
    await message.answer("Изменения сохранены. Ваше объявление:\n\n" + ad_text, reply_markup=confirm_kb)

@dp.message(F.text == "⬆️Показать меню")
async def show_menu_kb(message: Message, state: FSMContext):
    await state.update_data(showed_kb = True)
    current_state = await state.get_state()
    if current_state == ViewingVacancies.viewing_vacancy:
        await message.answer("Меню показано", reply_markup = vacancy_kb_showed)

    elif current_state == ViewingAds.viewing_ad:
    
        await message.answer("Меню показано", reply_markup = ads_kb_showed)
    else:
        await handle_main_text(message, state)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

@dp.message(F.text == "⬇️Скрыть меню")
async def hide_menu_kb(message: Message, state: FSMContext):
    await state.update_data(showed_kb = False)
    current_state = await state.get_state()
    if current_state == ViewingVacancies.viewing_vacancy:
        await message.answer("Меню скрыто", reply_markup = vacancy_kb_hided)

    elif current_state == ViewingAds.viewing_ad:
    
        await message.answer("Меню скрыто", reply_markup = ads_kb_hided)
    else:
        await handle_main_text(message, state)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
#################################################

#  ВАКАНСИИ

################################################

# Обработчик начала создания вакансии
# Просмотр вакансий
@dp.message(F.text == "👔Вакансии")
async def show_vacancies(message: Message, state: FSMContext):
    await state.update_data(
        viewing_vacancy=0,
        saved_vacancies=get_saved_vacancies(get_user_id_by_tg_id(message.from_user.id)),
        only_saved=False,
        vacancy_filters={
            'salary_min': None,
            'salary_max': None,
            'user_id': get_user_id_by_tg_id(message.from_user.id)
        },
        author = 'не указан'
    )
    await state.set_state(ViewingVacancies.viewing_vacancy)
    await display_current_vacancy(message, state)

async def display_current_vacancy(message: Message, state: FSMContext):
    try:
        # Получаем данные с защитой по умолчанию
        data = await state.get_data()
        vacancies = get_vacancies() or []  # Защита от None
        
        # Инициализация фильтров по умолчанию
        vacancy_filters = data.get('vacancy_filters', {
            'salary_min': None,
            'salary_max': None
        })
        
        saved_vacancies = data.get('saved_vacancies', [])
        print(saved_vacancies)
        only_saved = data.get('only_saved', False)
        current_index = max(0, min(data.get("viewing_vacancy", 0), len(vacancies) - 1))
        
        # Применяем фильтры с защитой
        filtered_vacancies = []

        print(f"Filters: {vacancy_filters}")
        print(f"Only saved: {only_saved}")
        print(f"Saved vacancies: {saved_vacancies}")
        print(f"Total vacancies before filtering: {len(vacancies)}")
        for v in vacancies:
            print (v)
            try:

                salary_ok = (
                    (vacancy_filters.get('salary_min') is None or v[4] >= vacancy_filters['salary_min']) and
                    (vacancy_filters.get('salary_max') is None or v[4] <= vacancy_filters['salary_max'])
                )

                # if data['author'] != 'не указан' and v[8] != data['author']:
                #     author_ok = True
                # else:
                #     author_ok = False
        
                # if only_saved:
                #     saved_ok = (v[0],) in saved_vacancies
                # else:
                #     saved_ok = True
                # saved_ok = not only_saved or (v[0],) in saved_vacancies



                # author_ok = vacancy_filters.get('user_id') is None or v[8] == vacancy_filters['user_id']

                # if salary_ok and saved_ok and author_ok:
                filtered_vacancies.append(v)
            except IndexError:
                continue
        
        if not filtered_vacancies:
            await message.answer("Нет вакансий, соответствующих фильтрам", 
                               reply_markup=vacancy_kb_showed)
            return
        
        current_index = min(current_index, len(filtered_vacancies) - 1)
        vacancy = filtered_vacancies[current_index]
        
        # Проверка структуры вакансии
        if len(vacancy) < 9:
            await message.answer("Ошибка формата данных вакансии")
            return
        
        # Увеличиваем просмотры
        increment_vacancy_views(vacancy[0])
        
        # Проверка владельца
        user_id = get_user_id_by_tg_id(message.from_user.id)
        user_vacancies = get_user_vacancies(user_id) or []
        is_owner = (vacancy[0],) in user_vacancies
        
        # Проверка сохранённости
        is_saved = (vacancy[0],) in saved_vacancies
        
        # Получение статистики
        stats = get_vacancy_statistics(vacancy[0]) or (0, 0)  # Защита от None
        
        # Формирование текста
        vacancy_text = (
            f"<b>Название</b>: {vacancy[2]}\n"
            f"<b>Описание</b>: {vacancy[3]}\n"
            f"<b>Зарплата</b>: {vacancy[4]}\n"
            # f"<b>Требования</b>: {vacancy[5]}\n"
            f"<b>Контакты</b>: {vacancy[6]}\n\n"
            
        )
        stat_text = (
            f"📅Дата публикации: {await format_date(vacancy[7])}\n"
            f"👁 Просмотров: {stats[0]} | ❤️ Сохранений: {stats[1]}"
        )
        # Отправка сообщений

        if data.get("ad_msg_id"):
            await bot.delete_message(chat_id=message.chat.id, message_id=data.get("ad_msg_id"))
        if data.get("stat_msg_id"):
            await bot.delete_message(chat_id=message.chat.id, message_id=data.get("stat_msg_id"))

        ad_msg = await message.answer(vacancy_text, reply_markup=vacancy_ikb(is_saved, is_owner))
        stat_msg = await message.answer(stat_text, reply_markup=vacancy_kb_showed if data.get("showed_kb", True) else vacancy_kb_hided)
        
        await state.update_data({"ad_msg_id" :ad_msg.message_id,
        "stat_msg_id" : stat_msg.message_id})

        # Обновление состояния
        await state.update_data(
            current_vacancy_id=vacancy[0],
            viewing_vacancy=current_index,
            filtered_vacancies=[v[0] for v in filtered_vacancies],
            is_owner=is_owner,
            is_saved=is_saved
        )
        
    except Exception as e:
        logging.error(f"Error in display_current_vacancy: {e}")
        await message.answer("Произошла ошибка при отображении вакансии")

# Фильтры
@dp.message(F.text == "💰Зарплата от")
async def set_salary_min(message: Message, state: FSMContext):
    await state.set_state(ViewingVacancies.salary_min)
    await message.answer("Введите минимальную зарплату:", reply_markup=back_kb)

@dp.message(ViewingVacancies.salary_min)
async def process_salary_min(message: Message, state: FSMContext):
    if message.text == "❌Назад":
        await state.set_state(ViewingVacancies.viewing_vacancy)
        await display_current_vacancy(message, state)
        return
    
    try:
        salary = int(message.text)
        data = await state.get_data()
        data['vacancy_filters']['salary_min'] = salary
        await state.update_data(data)
        await message.answer(f"Установлена минимальная зарплата: {salary}")
    except ValueError:
        await message.answer("Пожалуйста, введите число!")
    
    await state.set_state(ViewingVacancies.viewing_vacancy)
    await display_current_vacancy(message, state)


# Фильтры
@dp.message(F.text == "💰Зарплата до")
async def set_salary_min(message: Message, state: FSMContext):
    await state.set_state(ViewingVacancies.salary_min)
    await message.answer("Введите максимальную зарплату:", reply_markup=back_kb)

@dp.message(ViewingVacancies.salary_min)
async def process_salary_min(message: Message, state: FSMContext):
    if message.text == "❌Назад":
        await state.set_state(ViewingVacancies.viewing_vacancy)
        await display_current_vacancy(message, state)
        return
    
    try:
        salary = int(message.text)
        data = await state.get_data()
        data['vacancy_filters']['salary_max'] = salary
        await state.update_data(data)
        await message.answer(f"Установлена максимальная зарплата: {salary}")
    except ValueError:
        await message.answer("Пожалуйста, введите число!")
    
    await state.set_state(ViewingVacancies.viewing_vacancy)
    await display_current_vacancy(message, state)
# Аналогично для salary_max...

# Сохранение вакансий
# Хендлер кнопки "Назад" (предыдущая вакансия)
@dp.callback_query(F.data == "prev_vacancy")
async def prev_vacancy_handler(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        current_index = data.get("viewing_vacancy", 0)
        filtered_vacancies = data.get("filtered_vacancies", [])
        
        if not filtered_vacancies:
            await callback.answer("Нет доступных вакансий", show_alert=True)
            return
        
        new_index = (current_index - 1) % len(filtered_vacancies)
        await state.update_data(viewing_vacancy=new_index)
        
        await display_current_vacancy(callback.message, state)
        await callback.answer()
    except Exception as e:
        logging.error(f"Error in prev_vacancy_handler: {e}")
        await callback.answer("Ошибка при загрузке вакансии", show_alert=True)

# Хендлер кнопки "Вперед" (следующая вакансия)
@dp.callback_query(F.data == "next_vacancy")
async def next_vacancy_handler(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        current_index = data.get("viewing_vacancy", 0)
        filtered_vacancies = data.get("filtered_vacancies", [])
        
        if not filtered_vacancies:
            await callback.answer("Нет доступных вакансий", show_alert=True)
            return
        
        new_index = (current_index + 1) % len(filtered_vacancies)
        await state.update_data(viewing_vacancy=new_index)
        
        await display_current_vacancy(callback.message, state)
        await callback.answer()
    except Exception as e:
        logging.error(f"Error in next_vacancy_handler: {e}")
        await callback.answer("Ошибка при загрузке вакансии", show_alert=True)

# Хендлер кнопки "Добавить в избранное"
@dp.callback_query(F.data == "add_saved_vacancy")
async def add_saved_vacancy_handler(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        vacancy_id = data.get("current_vacancy_id")
        user_id = get_user_id_by_tg_id(callback.from_user.id)
        
        if not vacancy_id or not user_id:
            await callback.answer("Ошибка: данные не найдены", show_alert=True)
            return
        
        add_vacancy_to_saved(vacancy_id, user_id)
        
        # Обновляем состояние
        await state.update_data(
            is_saved=True,
            saved_vacancies=get_saved_vacancies(user_id)
        )
        
        await callback.answer("Вакансия добавлена в избранное")
        await display_current_vacancy(callback.message, state)
    except Exception as e:
        logging.error(f"Error in add_saved_vacancy_handler: {e}")
        await callback.answer("Ошибка при добавлении в избранное", show_alert=True)

# Хендлер кнопки "Удалить из избранного"
@dp.callback_query(F.data == "remove_saved_vacancy")
async def remove_saved_vacancy_handler(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        vacancy_id = data.get("current_vacancy_id")
        user_id = get_user_id_by_tg_id(callback.from_user.id)
        
        if not vacancy_id or not user_id:
            await callback.answer("Ошибка: данные не найдены", show_alert=True)
            return
        
        remove_vacancy_from_saved(vacancy_id, user_id)
        
        # Обновляем состояние
        await state.update_data(
            is_saved=False,
            saved_vacancies=get_saved_vacancies(user_id)
        )
        
        await callback.answer("Вакансия удалена из избранного")
        await display_current_vacancy(callback.message, state)
    except Exception as e:
        logging.error(f"Error in remove_saved_vacancy_handler: {e}")
        await callback.answer("Ошибка при удалении из избранного", show_alert=True)

# Хендлер кнопки "Редактировать" (для своих вакансий)
@dp.callback_query(F.data == "edit_vacancy")
async def edit_vacancy_handler(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        
        # Проверяем, что вакансия принадлежит пользователю
        if not data.get("is_owner", False):
            await callback.answer("Вы не можете редактировать эту вакансию", show_alert=True)
            return
        
        vacancy = get_vacancy_by_id(data['current_vacancy_id'])
        if not vacancy:
            await callback.answer("Вакансия не найдена", show_alert=True)
            return
        
        # Сохраняем данные вакансии для редактирования
        await state.update_data(
            editing_vacancy={
                'vacancy_id': vacancy[0],
                'title': vacancy[2],
                'description': vacancy[3],
                'salary': vacancy[4],
                'requirements': vacancy[5],
                'contacts': vacancy[6]
            }
        )
        
        await callback.message.answer(
            "Выберите поле для редактирования:",
            reply_markup=vacancy_edit_kb
        )
        await state.set_state(NewVacancy.change)
        await callback.answer()
    except Exception as e:
        logging.error(f"Error in edit_vacancy_handler: {e}")
        await callback.answer("Ошибка при редактировании вакансии", show_alert=True)

# Хендлер кнопки "Связаться" (для чужих вакансий)
@dp.callback_query(F.data == "get_vacancy_contact")
async def get_vacancy_contact_handler(callback: CallbackQuery, state: FSMContext):
    # try:
    data = await state.get_data()
    vacancy_id = data.get("current_vacancy_id")

    author_data = get_contact_by_user_id(data.get('user_id'))
    
    author_name = author_data[0][0]
    # author_nickname = author_data[0][1]
    author_tg_id = author_data[0][2]
    author_phone = author_data[0][3]
    
    try:
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text=f"Автор объявления: {f'[({author_name})](tg://user?id={author_tg_id})'}",
            parse_mode="MarkdownV2"
            )
    except Exception as e:
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text=f"Номер телефона автора: {f'{author_phone} - ({author_name})'}",
            parse_mode="MarkdownV2"
            )
        
        
        # if not vacancy_id:
        #     await callback.answer("Вакансия не найдена", show_alert=True)
        #     return
        
        # Получаем контактные данные вакансии
        # vacancy = get_vacancy_by_id(vacancy_id)
        # if not vacancy or len(vacancy) < 7:
        #     await callback.answer("Контактные данные не найдены", show_alert=True)
        #     return
        
        # contacts = vacancy[6]  # Контакты находятся по индексу 6
        
        # Отправляем контакты пользователю
        # await callback.message.answer(
        #     f"📞 Контактные данные для связи:\n{contacts}",
        #     reply_markup=ReplyKeyboardRemove()
        # )
        await callback.answer()
    # except Exception as e:
    #     logging.error(f"Error in get_vacancy_contact_handler: {e}")
    #     await callback.answer("Ошибка при получении контактов", show_alert=True)

# Создание вакансии
@dp.message(F.text == "✔️Разместить вакансию")
async def new_vacancy(message: Message, state: FSMContext):
    await state.clear()

    await state.set_state(NewVacancy.title)
    await message.answer("Введите название вакансии:")

@dp.message(NewVacancy.title)
async def process_vacancy_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(NewVacancy.description)
    await message.answer("Введите описание вакансии:")

@dp.message(NewVacancy.description)
async def process_vacancy_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(NewVacancy.salary)
    await message.answer("Укажите зарплату (число):")

@dp.message(NewVacancy.salary)
async def process_vacancy_salary(message: Message, state: FSMContext):
    try:
        salary = int(message.text)
        
        # await message.answer("Укажите контактные данные для связи:")
        # await state.set_state(NewVacancy.requirements)
        # await message.answer("Укажите требования к кандидату:")
    except ValueError:
        await message.answer("Пожалуйста, введите число!")
    await state.update_data(salary=salary)
    await state.set_state(NewVacancy.contacts)
    print('зарплата ввелась')

@dp.message(NewVacancy.requirements)
async def process_vacancy_requirements(message: Message, state: FSMContext):
    # await state.update_data(requirements=message.text)
    await state.set_state(NewVacancy.contacts)
    # await message.answer("Укажите контактные данные для связи:")

@dp.message(NewVacancy.contacts)
async def process_vacancy_contacts(message: Message, state: FSMContext):
    # await state.update_data(contacts=message.text)
    data = await state.get_data()
    print('подтверждение')
    preview_text = (
        f"<b>Название</b>: {data['title']}\n"
        f"<b>Описание</b>: {data['description']}\n"
        f"<b>Зарплата</b>: {data['salary']}\n"
        # f"<b>Требования</b>: {data['requirements']}\n"
        # f"<b>Контакты</b>: {data['contacts']}\n\n"
        "Ваша вакансия выглядит так, всё верно?"
    )
    
    await message.answer(preview_text, reply_markup=confirm_kb)
    await state.set_state(NewVacancy.confirm)

@dp.message(NewVacancy.confirm, F.text == "✅Разместить")
async def publish_vacancy(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = get_user_id_by_tg_id(message.from_user.id)
    
    vacancy_id = insert_new_vacancy(
        user_id=user_id,
        title=data['title'],
        description=data['description'],
        salary=data['salary'],
        # requirements=data['requirements'],
        requirements='1',
        # contacts=data['contacts']
        contacts = '1'
    )
    
    await message.answer("✅ Вакансия успешно опубликована!", reply_markup=main_kb)
    await state.clear()

@dp.message(F.text == "Мои вакансии")
async def show_my_vacancies(message: Message, state: FSMContext):
    user_id = get_user_id_by_tg_id(message.from_user.id)
    await state.update_data(
        viewing_vacancy=0,
        saved_vacancies=get_saved_vacancies(user_id),
        only_saved=False,
        vacancy_filters={
            'user_id': user_id,  # Фильтр по автору
            'salary_min': None,
            'salary_max': None
        },
        author = user_id
    )
    await state.set_state(ViewingVacancies.viewing_vacancy)
    await display_current_vacancy(message, state)

@dp.message(F.text == "Сохраненные вакансии")
async def show_saved_vacancies(message: Message, state: FSMContext):
    user_id = get_user_id_by_tg_id(message.from_user.id)
    await state.update_data(
        viewing_vacancy=0,
        saved_vacancies=get_saved_vacancies(user_id),
        only_saved=True,  # Включаем фильтр только сохраненных
        vacancy_filters={
            'user_id': 'не указан',
            'salary_min': None,
            'salary_max': None
        }
    )
    await state.set_state(ViewingVacancies.viewing_vacancy)
    await display_current_vacancy(message, state)


# Start the bot
async def main():
    try:
        await dp.start_polling(bot)
    finally:
        close_connection()

if __name__ == '__main__':
    asyncio.run(main())