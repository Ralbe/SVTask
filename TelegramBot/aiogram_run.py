import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram import BaseMiddleware

from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from utils.stateform import NewAds, CheckMessage, ViewingAdsStates
from DataBase.UserDB import add_category, get_ads, insert_new_ad, get_category_id, get_location_id, close_connection, get_user_id_by_tg_id, add_user_by_tg_id
from keyboards.keyboards import main_kb, ads_kb, confirm_kb, red_kb, reg_kb, back_kb, filter_kb
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

# print(ads)
# current_ad_index = 0

# bot_restarted = True

# class ResetStateMiddleware(BaseMiddleware):
#     async def __call__(self, handler, event: Message, data: dict):
#         global bot_restarted

#         if bot_restarted:
#             state: FSMContext = data.get("state")
#             if state:
#                 await state.clear()
#             bot_restarted = False
#         return await handler(event, data)

# dp.message.middleware(ResetStateMiddleware())


@dp.message(Command("start"))
async def handle_menu_command(message: Message, state: FSMContext):
    await state.clear()
    get_user_id_by_tg_id(message.from_user.id) #если нет добавить
    await message.answer("Добро пожаловать.", reply_markup=reg_kb) 


@dp.message(F.text == "🏠На главную")
async def handle_main_text(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите желаемый раздел.", reply_markup=main_kb)


@dp.message(F.text == "🕶Объявления")
async def show_ads(message: Message, state: FSMContext):
    await message.answer("Выберите интересующий вариант.", reply_markup=ads_kb)
    await state.update_data(viewing_ad=0)  # Инициализируем индекс
    await state.set_state(ViewingAdsStates.viewing_ad)
    await display_current_ad(message, state)  # Показываем первое объявление

async def display_current_ad(message: Message, state: FSMContext):
    data = await state.get_data()
    current_index = data.get("viewing_ad", 0)
    
    # Корректируем индекс если вышел за границы
    if current_index >= len(ads):
        current_index = 0
        await state.update_data(viewing_ad=0)
    elif current_index < 0:
        current_index = len(ads) - 1
        await state.update_data(viewing_ad=len(ads) - 1)
    
    ad = ads[current_index]
    ad_text = (f"<b>Категория</b>: {ad[3]}\n"
               f"<b>Местоположение</b>: {ad[4]}\n"
               f"<b>Заголовок</b>: {ad[1]}\n"
               f"<b>Описание</b>: {ad[2]}\n"
               f"<b>Цена</b>: {ad[5]}₽")
    await message.answer(ad_text, reply_markup=ads_kb)

@dp.message(F.text == "Вперед➡️", ViewingAdsStates.viewing_ad)
async def next_ad(message: Message, state: FSMContext):
    data = await state.get_data()
    current_index = data.get("viewing_ad", 0)
    
    new_index = current_index + 1
    if new_index >= len(ads):
        new_index = 0
    
    await state.update_data(viewing_ad=new_index)
    await display_current_ad(message, state)

@dp.message(F.text == "⬅️Назад", ViewingAdsStates.viewing_ad)
async def prev_ad(message: Message, state: FSMContext):
    data = await state.get_data()
    current_index = data.get("viewing_ad", 0)
    
    new_index = current_index - 1
    if new_index < 0:
        new_index = len(ads) - 1
    
    await state.update_data(viewing_ad=new_index)
    await display_current_ad(message, state)

# @dp.message(F.text == "⚙️Фильтры")
# async def filters_command(message: types.Message, state: FSMContext):
#     # Инициализируем данные фильтра
#     await state.update_data(
#         category=None,
#         city=None,
#         price_min=None,
#         price_max=None
#     )
    
#     # Отправляем клавиатуру фильтров
#     await message.answer(
#         "Настройте параметры поиска:",
#         reply_markup=filter_kb
#     )

# # Хендлеры для обработки выбора фильтров
# @dp.message(F.text == "📁 Категория")
# async def set_category(message: types.Message):
#     await ViewingAdsStates.waiting_for_category.set()
#     await message.answer("Выберите категорию:", reply_markup=types.ReplyKeyboardRemove())

# @dp.message(ViewingAdsStates.waiting_for_category)
# async def process_category(message: types.Message, state: FSMContext):
#     await state.update_data(category=message.text)
#     await state.reset_state(with_data=False)
#     await message.answer(f"Категория установлена: {message.text}", reply_markup=filter_kb)

# @dp.message(F.text == "🏙️ Город")
# async def set_city(message: types.Message):
#     await ViewingAdsStates.waiting_for_city.set()
#     await message.answer("Введите город:", reply_markup=types.ReplyKeyboardRemove())

# @dp.message(ViewingAdsStates.waiting_for_city)
# async def process_city(message: types.Message, state: FSMContext):
#     await state.update_data(city=message.text)
#     await state.reset_state(with_data=False)
#     await message.answer(f"Город установлен: {message.text}", reply_markup=filter_kb)

# @dp.message(F.text == "💰 Цена от")
# async def set_price_min(message: types.Message):
#     await ViewingAdsStates.waiting_for_price_min.set()
#     await message.answer("Введите минимальную цену:", reply_markup=types.ReplyKeyboardRemove())

# @dp.message(ViewingAdsStates.waiting_for_price_min)
# async def process_price_min(message: types.Message, state: FSMContext):
#     try:
#         price = int(message.text)
#         await state.update_data(price_min=price)
#         await state.reset_state(with_data=False)
#         await message.answer(f"Минимальная цена установлена: {price}", reply_markup=filter_kb)
#     except ValueError:
#         await message.answer("Пожалуйста, введите число!")

# @dp.message(F.text == "💰 Цена до")
# async def set_price_max(message: types.Message):
#     await ViewingAdsStates.waiting_for_price_max.set()
#     await message.answer("Введите максимальную цену:", reply_markup=types.ReplyKeyboardRemove())

# @dp.message(ViewingAdsStates.waiting_for_price_max)
# async def process_price_max(message: types.Message, state: FSMContext):
#     try:
#         price = int(message.text)
#         await state.update_data(price_max=price)
#         await state.reset_state(with_data=False)
#         await message.answer(f"Максимальная цена установлена: {price}", reply_markup=filter_kb)
#     except ValueError:
#         await message.answer("Пожалуйста, введите число!")

# # Хендлер для завершения настройки фильтров
# @dp.message(F.text == "✅ Готово")
# async def finish_filters(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     await message.answer(
#         f"Фильтры установлены:\n"
#         f"Категория: {data.get('category', 'не указана')}\n"
#         f"Город: {data.get('city', 'не указан')}\n"
#         f"Цена от: {data.get('price_min', 'не указана')}\n"
#         f"Цена до: {data.get('price_max', 'не указана')}",
#         reply_markup=types.ReplyKeyboardRemove()
#     )
#     await state.finish()


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
    await state.set_state(NewAds.waiting_for_confirm)
    

@dp.message(NewAds.waiting_for_confirm)
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
    elif message.text == "✍️Редактировать":
        await state.set_state(NewAds.waiting_for_change)
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
        

@dp.message(NewAds.waiting_for_change)
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
        await state.set_state(NewAds.waiting_for_confirm)
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
        await state.set_state(NewAds.waiting_for_change)
        await message.answer("Выберите поле для редактирования:", reply_markup=red_kb)
        return
    
    data = await state.get_data()
    field_name = data.get("editing_field")
    
    if not field_name:
        await message.answer("Ошибка: поле для редактирования не определено")
        await state.set_state(NewAds.waiting_for_change)
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
    await state.set_state(NewAds.waiting_for_confirm)
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