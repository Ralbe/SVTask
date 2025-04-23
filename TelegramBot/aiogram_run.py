import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram import BaseMiddleware

from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from utils.stateform import NewAds, CheckMessage, ViewingAds, ViewingOwnAds, Profile
from DataBase.UserDB import (add_category, get_ads, insert_new_ad, get_category_id, get_location_id, close_connection, 
                            get_user_id_by_tg_id, set_user_data, get_user_data, get_categories, get_saved_by_user, 
                            remove_ad_from_saved, add_ad_in_saved)
from keyboards.keyboards import (main_kb, ads_kb_if_saved, ads_kb_if_not_saved, confirm_kb, red_kb, back_kb, filter_kb, 
                                set_user_data_kb, ads_ikb)
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode


# Инициализация бота и диспетчера
# API_TOKEN = '7754829803:AAF9bmNcb635GC0emlEjkd3x8_YI75IJYz4' # main
API_TOKEN = '7588331682:AAHWaQdhjofYczgtFvFj3-EPYBzxR6dCKUY' # test
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(
    parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

ads = get_ads()

@dp.message(Command("start"))
async def handle_menu_command(message: Message, state: FSMContext):
    await state.clear()
    get_user_id_by_tg_id(message.from_user.id) #если нет добавить
    data = get_user_data(message.from_user.id)
    await state.update_data({"first_name":data[0][0], "second_name":data[0][1], "phone":data[0][2],"email":data[0][3]})
    await enter_profile_mode(message, state)

@dp.message(F.text == "🏠На главную")
async def handle_main_text(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите желаемый раздел.", reply_markup=main_kb)

#######################################################################

async def enter_profile_mode(message: Message, state: FSMContext):
    # Получаем текущие данные из FSM (если есть)
    
    data = await state.get_data()
    # print(data)
    # Формируем сообщение с текущими данными


    profile_info = (
        "⚙️ <b>Ваш профиль:</b>\n\n"
        f"👤 <b>Имя:</b> {data.get('first_name', 'не указано')}\n"
        f"👥 <b>Фамилия:</b> {data.get('second_name', 'не указано')}\n"
        f"📧 <b>Email:</b> {data.get('email', 'не указан')}\n"
        f"📞 <b>Телефон:</b> {data.get('phone', 'не указан')}\n\n"
        "Выберите поле для редактирования:"
    )
    
    # Отправляем сообщение с клавиатурой
    await message.answer(
        text=profile_info,
        reply_markup=set_user_data_kb  # Предполагается, что клавиатура уже импортирована
    )
    
    # Можно сбросить состояние (если не нужно держать конкретное состояние)
    await state.set_state(None)

@dp.message(F.text == "👤Профиль")
async def profile_command(message: Message, state: FSMContext):
    data = get_user_data(message.from_user.id)
    await state.update_data({"first_name":data[0][0], "second_name":data[0][1], "phone":data[0][2],"email":data[0][3]})
    await enter_profile_mode(message, state)
   
# Хендлеры для обработки редактирования профиля
@dp.message(F.text == "👤Имя")
async def set_first_name(message: types.Message, state: FSMContext):
    await state.set_state(Profile.first_name)
    await message.answer("Введите ваше имя:", reply_markup=types.ReplyKeyboardRemove())

@dp.message(Profile.first_name)
async def process_first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer(f"Имя установлено: {message.text}", reply_markup=set_user_data_kb)
    await enter_profile_mode(message, state)

@dp.message(F.text == "👥Фамилия")
async def set_second_name(message: types.Message, state: FSMContext):
    await state.set_state(Profile.second_name)
    await message.answer("Введите вашу фамилию:", reply_markup=types.ReplyKeyboardRemove())

@dp.message(Profile.second_name)
async def process_second_name(message: types.Message, state: FSMContext):
    await state.update_data(second_name=message.text)
    await message.answer(f"Фамилия установлена: {message.text}", reply_markup=set_user_data_kb)
    await enter_profile_mode(message, state)

@dp.message(F.text == "📧Email")
async def set_email(message: types.Message, state: FSMContext):
    await state.set_state(Profile.email)
    await message.answer("Введите ваш email:", reply_markup=types.ReplyKeyboardRemove())

@dp.message(Profile.email)
async def process_email(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer(f"Email установлен: {message.text}", reply_markup=set_user_data_kb)
    await enter_profile_mode(message, state)

@dp.message(F.text == "📞Телефон")
async def set_phone(message: types.Message, state: FSMContext):
    await state.set_state(Profile.phone)
    await message.answer("Введите ваш телефон:", reply_markup=types.ReplyKeyboardRemove())

@dp.message(Profile.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer(f"Телефон установлен: {message.text}", reply_markup=set_user_data_kb)
    await enter_profile_mode(message, state)

# Хендлер для сохранения профиля
@dp.message(F.text == "✅Сохранить профиль")
async def save_profile(message: types.Message, state: FSMContext):
    data = await state.get_data()
    # Вызываем функцию для сохранения данных профиля
    set_user_data(
        first_name=data.get('first_name'),
        second_name=data.get('second_name'),
        email=data.get('email'),
        phone=data.get('phone'),
        tg_id = message.from_user.id
    )
    await message.answer("Профиль успешно сохранён!", reply_markup=set_user_data_kb)

# Хендлер для сброса профиля
@dp.message(F.text == "❌Сбросить профиль")
async def reset_profile(message: types.Message, state: FSMContext):
    await state.set_data({})  # Очищаем все данные профиля
    await message.answer("Данные профиля сброшены", reply_markup=set_user_data_kb)

#######################################################################

@dp.message(F.text == "🕶Объявления")
async def show_ads(message: Message, state: FSMContext):
    await message.answer("Выберите интересующий вариант.", reply_markup=types.ReplyKeyboardRemove())
    await state.update_data(viewing_ad=0)  # Инициализируем индекс
    await state.update_data(author = 'не указан')
    await state.update_data(only_saved = False)
    # await state.update_data(ad_id = None)
    await state.update_data(saved_ads = get_saved_by_user(get_user_id_by_tg_id(message.from_user.id)))
    await state.set_state(ViewingAds.viewing_ad)
    await display_current_ad(message, state)  # Показываем первое объявление

async def check_ad_filters(ad: tuple, filters: dict, state: FSMContext) -> bool:
    """Проверяет, соответствует ли объявление установленным фильтрам."""
    # Получаем данные из объявления (предполагаем, что ad[3] - категория, ad[4] - город, ad[5] - цена)
    ad_id = ad[0]
    ad_author = ad[1]
    ad_category = ad[4]
    ad_city = ad[5]
    ad_price = ad[6]

    data = await state.get_data()
    liked_list = data.get("saved_ads")
    only_saved = data.get("only_saved")
    print((ad_id,),"__________________________", only_saved, "|",liked_list)

    # liked = False

    # if ((ad[0],)) in liked_list:
    #     liked = True

    if only_saved and (ad[0],) not in liked_list:
        return False
        
    if 'author' in filters and filters['author'] !='не указан'and ad_author != filters['author']:
        return False
    if 'category' in filters and filters['category'] != 'не указана' and ad_category != filters['category']:
        return False
    if 'city' in filters and filters['city'] != 'не указан' and ad_city != filters['city']:
        return False
    if 'price_min' in filters and filters['price_min'] != 'не указана' and ad_price < int(filters['price_min']):
        return False
    if 'price_max' in filters and filters['price_max'] != 'не указана' and ad_price > int(filters['price_max']):
        return False

    
    return True

async def find_next_filtered_ad(current_index: int, filters: dict, state: FSMContext, forward: bool = True) -> int:
    """Находит следующее объявление, соответствующее фильтрам."""
    step = 1 if forward else -1
    checked = 0  # Чтобы избежать бесконечного цикла
    
    total_ads = len(ads)
    
    if total_ads == 0:
        return -1  # Нет объявлений

    while checked < len(ads):
        current_index = (current_index + step) % len(ads)
        if current_index < 0:
            current_index = len(ads) - 1
        
        if await check_ad_filters(ads[current_index], filters, state):
            return current_index
        
        checked += 1
    
    return current_index  # Если ничего не найдено, возвращаем исходный индекс

async def display_current_ad(message: Message, state: FSMContext):
    data = await state.get_data()
    current_index = data.get("viewing_ad", 0)
    filters = {
        'category': data.get('category', 'не указана'),
        'city': data.get('city', 'не указан'),
        'price_min': data.get('price_min', 'не указана'),
        'price_max': data.get('price_max', 'не указана'),
        'author':data.get('author','не указан')
    }
    
    # Проверяем текущее объявление на соответствие фильтрам
    if not await check_ad_filters(ads[current_index], filters, state):
        # Если текущее не подходит, ищем следующее подходящее
        current_index = await find_next_filtered_ad(current_index, filters, state, forward=True)
        await state.update_data(viewing_ad=current_index)
    
    ad = ads[current_index]

    liked = False
    liked_list = data.get("saved_ads")
    if ((ad[0],)) in liked_list:
        liked = True
    # print(liked_list)
    # print (liked)

    ad_text = (f"<b>Категория</b>: {ad[4]}\n"
               f"<b>Местоположение</b>: {ad[5]}\n"
               f"<b>Заголовок</b>: {ad[2]}\n"
               f"<b>Описание</b>: {ad[3]}\n"
               f"<b>Цена</b>: {ad[6]}₽")
    await message.answer(ad_text, reply_markup=ads_kb_if_saved if liked else ads_kb_if_not_saved)


    print(f"Всего объявлений: {len(ads)}")
    print(f"Текущий индекс: {current_index}")
    print(f"Фильтры: {filters}")
    print(f"Объявление {current_index}: {ads[current_index]}")
    print(f"Прошло фильтры: {await check_ad_filters(ads[current_index], filters, state)}")

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
    
    # Ищем следующее объявление, соответствующее фильтрам
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
    
    # Ищем предыдущее объявление, соответствующее фильтрам
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
    f"Цена до: {data.get('price_max', 'не указана')}",reply_markup=filter_kb
    )

async def enter_filter_mode(message: Message, state: FSMContext):
    # (1) Устанавливаем состояние
    await state.set_state(ViewingAds.filters)
    await show_filters(message, state)

@dp.message(F.text == "⚙️Фильтры")
async def filters_command(message: Message, state: FSMContext):
    await enter_filter_mode(message, state)
   
# Хендлеры для обработки выбора фильтров
@dp.message(F.text == "📁Категория")
async def set_category(message: types.Message, state: FSMContext):

    await state.set_state(ViewingAds.category)
    await message.answer("Выберите категорию: ", reply_markup=types.ReplyKeyboardRemove())

@dp.message(ViewingAds.category)
async def process_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    # await state.reset_state(with_data=False)

    await message.answer(f"Категория установлена: {message.text}", reply_markup=filter_kb)
    await enter_filter_mode(message, state)

@dp.message(F.text == "🏙️Город")
async def set_city(message: types.Message, state: FSMContext):
    
    await state.set_state(ViewingAds.city)
    await message.answer("Введите город:", reply_markup=types.ReplyKeyboardRemove())

@dp.message(ViewingAds.city)
async def process_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    # await state.reset_state(with_data=False)
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
        # await state.reset_state(with_data=False)
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
        # await state.reset_state(with_data=False)
        await message.answer(f"Максимальная цена установлена: {price}", reply_markup=filter_kb)
    except ValueError:
        await message.answer("Пожалуйста, введите число!")
    await enter_filter_mode(message, state)

@dp.message(F.text == "❤️В избранном")
async def del_from_saved(message: Message, state: FSMContext):
    data = await state.get_data()
    ad = ads[data["viewing_ad"]]

    remove_ad_from_saved(ad[0], get_user_id_by_tg_id(message.from_user.id))
    await message.answer("Объявление удалено из избранного", reply_markup=ads_kb_if_not_saved)
    await message.delete()
    await state.update_data(saved_ads = get_saved_by_user(get_user_id_by_tg_id(message.from_user.id)))
    # await display_current_ad(message, state)

@dp.message(F.text == "♡Добавить в избранное")
async def del_from_saved(message: Message, state: FSMContext):
    data = await state.get_data()
    ad = ads[data["viewing_ad"]]
    add_ad_in_saved(ad[0], get_user_id_by_tg_id(message.from_user.id))
    await message.answer("Объявление добавлено в избранное", reply_markup=ads_kb_if_saved)
    await message.delete()
    await state.update_data(saved_ads = get_saved_by_user(get_user_id_by_tg_id(message.from_user.id)))
    # await display_current_ad(message, state)

@dp.message(F.text == "❌Сбросить фильтры")
async def finish_filters(message: types.Message, state: FSMContext):

    data = await state.get_data()
    await state.set_data({"viewing_ad": data.get("viewing_ad")})

    await show_filters(message, state)

@dp.message(F.text == "Мои объявления")
async def show_ads(message: Message, state: FSMContext):
    # await message.answer("Выберите интересующий вариант.", reply_markup=types.ReplyKeyboardRemove())
    await state.update_data(viewing_ad=0)  # Инициализируем индекс
    await state.update_data(saved_ads = get_saved_by_user(get_user_id_by_tg_id(message.from_user.id)))
    await state.update_data(author = get_user_id_by_tg_id(message.from_user.id))
    await state.update_data(only_saved = False)
    await state.set_state(ViewingAds.viewing_ad)
    await display_current_ad(message, state)  # Показываем первоWе объявление

@dp.message(F.text == "Сохраненные объявления")
async def show_ads(message: Message, state: FSMContext):
    # await message.answer("Выберите интересующий вариант.", reply_markup=types.ReplyKeyboardRemove())
    await state.update_data(viewing_ad=0)  # Инициализируем индекс
    await state.update_data(saved_ads = get_saved_by_user(get_user_id_by_tg_id(message.from_user.id)))
    await state.update_data(only_saved = True)
    await state.set_state(ViewingAds.viewing_ad)
    await display_current_ad(message, state)  # Показываем первое объявление

@dp.message(F.text == "✔️Разместить объявление")
async def new_ads(message: Message, state: FSMContext):
    
    await state.clear()
    await state.set_state(NewAds)

    await message.reply("1) Введите название товара")
    await state.set_state(NewAds.title)

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
    await state.update_data(money=message.text)
    # Показываем предпросмотр объявления
    data = await state.get_data()
    ad_text = (f"<b>Заголовок</b>: {data['title']}\n"
                f"<b>Описание</b>: {data['description']}\n"
                f"<b>Категория</b>: {data['category']}\n"
                f"<b>Местоположение</b>: {data['location']}\n"
                f"<b>Цена</b>: {data['money']}₽")
    await message.answer("Ваше объявление будет выглядеть так:\n\n" + ad_text, 
                        reply_markup=confirm_kb)
    await state.set_state(NewAds.confirm)
    
@dp.message(NewAds.confirm)
async def message_okey(message: Message, state: FSMContext):
    if message.text == "✅Разместить":
        data = await state.get_data()
        tg_id = message.from_user.id
        category = data["category"]
        location = data["location"]
        title = data["title"]
        description = data["description"]
        money = data["money"]

        user_id = get_user_id_by_tg_id(tg_id)
        category_id = get_category_id(category)
        location_id = get_location_id(location)
        
        insert_new_ad(user_id, category_id, location_id, title, description, money)
        
        await message.reply("Ваше объявление размещено")
        await state.clear()
        await handle_menu_command(message, state)
        global ads
        ads = get_ads()
    elif message.text == "✍️Редактировать":
        await state.set_state(NewAds.change)
        await message.answer("Какую информацию вы хотите изменить?", reply_markup=red_kb)
    else:
        # Показываем предпросмотр объявления
        data = await state.get_data()
        ad_text = (f"<b>Заголовок</b>: {data['title']}\n"
                   f"<b>Описание</b>: {data['description']}\n"
                   f"<b>Категория</b>: {data['category']}\n"
                   f"<b>Местоположение</b>: {data['location']}\n"
                   f"<b>Цена</b>: {data['money']}₽")
        await message.answer("Ваше объявление будет выглядеть так:\n\n" + ad_text, 
                           reply_markup=confirm_kb)

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
        await message.answer("Пожалуйста, выберите поле для редактирования из списка", 
                            reply_markup=red_kb)
        return
    
    if choice == "Назад":
        await state.set_state(NewAds.confirm)
        data = await state.get_data()
        ad_text = (f"<b>Заголовок</b>: {data['title']}\n"
                   f"<b>Описание</b>: {data['description']}\n"
                   f"<b>Категория</b>: {data['category']}\n"
                   f"<b>Местоположение</b>: {data['location']}\n"
                   f"<b>Цена</b>: {data['money']}₽")
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
    
    # Обновляем данные
    await state.update_data({field_name: message.text})
    
    # Удаляем временное поле editing_field
    current_data = await state.get_data()
    if "editing_field" in current_data:
        new_data = current_data.copy()
        del new_data["editing_field"]
        await state.set_data(new_data)
    
    # Возвращаемся к подтверждению
    await state.set_state(NewAds.confirm)
    data = await state.get_data()
    ad_text = (f"<b>Заголовок</b>: {data['title']}\n"
               f"<b>Описание</b>: {data['description']}\n"
               f"<b>Категория</b>: {data['category']}\n"
               f"<b>Местоположение</b>: {data['location']}\n"
               f"<b>Цена</b>: {data['money']}₽")
    await message.answer("Изменения сохранены. Ваше объявление:\n\n" + ad_text, 
                        reply_markup=confirm_kb)


# Запуск бота
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

# Закрытие соединения с базой данных
close_connection()