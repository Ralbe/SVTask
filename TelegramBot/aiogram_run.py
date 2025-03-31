import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from utils.stateform import Form, NewAds
from DataBase.UserDB import get_ads, get_user_by_email, authenticate_user, add_user, insert_new_ad, get_category_id, get_location_id, close_connection
from keyboards.keyboards import main_kb, ads_kb, start_kb
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

# Инициализация бота и диспетчера
API_TOKEN = '7754829803:AAF9bmNcb635GC0emlEjkd3x8_YI75IJYz4'
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

ads = get_ads()
current_ad_index = 0

# Обработчик команды /start
@dp.message(F.text == "🔐Авторизация")
async def cmd_start(message: Message, state: FSMContext):
    current_state = await state.get_state()
    logging.info(f"Current state: {current_state}")
    if current_state == Form.authorized.state:
        await message.answer("Вы уже авторизованы.")
    else:
        await message.answer("Привет! Введите ваш email:")
        await state.set_state(Form.email)

# Обработчик состояния email
@dp.message(Form.email)
async def process_email(message: Message, state: FSMContext):
    email = message.text
    user = get_user_by_email(email)
    if "@" in email:
        if user:
            await state.update_data(email=email)
            await state.update_data(current_email=email)
            await message.answer("Введите ваш пароль для авторизации:")
            await state.set_state(Form.auth_password)
        else:
            await state.update_data(email=email)
            await message.answer("Теперь введите ваш логин:")
            await state.set_state(Form.login)
    else:
        await message.answer("Некорректный email. Попробуйте снова.")
        await state.set_state(Form.email)

# Обработчик состояния auth_password
@dp.message(Form.auth_password)
async def process_auth_password(message: Message, state: FSMContext):
    password = message.text
    user_data = await state.get_data()
    email = user_data['email']

    user = authenticate_user(email, password)

    if user:
        await state.update_data(user_id=user[0])
        await message.answer("Вы успешно авторизованы!")
        await state.set_state(Form.authorized)
        await authorized_action(message, state)
    else:
        await message.answer("Неверный пароль. Попробуйте снова. Введите вашу почту")
        await state.set_state(Form.email)

# Обработчик состояния login
@dp.message(Form.login)
async def process_login(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer("Теперь введите ваш пароль:")
    await state.set_state(Form.password)

# Обработчик состояния password
@dp.message(Form.password)
async def process_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    user_data = await state.get_data()
    email = user_data['email']
    login = user_data['login']
    password = user_data['password']

    add_user(login, password, email)

    await message.answer("Спасибо! Ваши данные сохранены.")
    await state.set_state(Form.authorized)
    await state.update_data(current_email=email)
    await authorized_action(message, state)

async def authorized_action(message: Message, state: FSMContext):
    check_state = await state.get_state()
    logging.info(f"Authorized action state: {check_state}")
    if check_state == Form.authorized.state:
        await message.answer("Выберите желаемый раздел.", reply_markup=main_kb)
    else:
        await message.answer("Пожалуйста, авторизуйтесь, чтобы получить доступ к меню.")

@dp.message(Command("menu"))
async def handle_menu_command(message: Message, state: FSMContext):
    await authorized_action(message, state)

@dp.message(F.text == "🏠На главную")
async def handle_main_text(message: Message, state: FSMContext):
    await authorized_action(message, state)

@dp.message(F.text == "🚪Выйти с аккаунта")
async def exit(message: Message, state: FSMContext):
    check_state = await state.get_state()
    if check_state == Form.authorized.state:
        user_data = await state.get_data()
        email = user_data.get('current_email')
        await message.answer(f"Вы вышли из аккаунта {email}", reply_markup=start_kb)
        await state.clear()
    else:
        await message.answer("Пожалуйста, авторизуйтесь, чтобы получить доступ к меню.")

@dp.message(F.text == "🕶Объявления")
async def show_ads(message: Message, state: FSMContext):
    check_state = await state.get_state()
    if check_state == Form.authorized.state:
        await message.answer("Выберите интересующий вариант.", reply_markup=ads_kb)
    else:
        await message.answer("Пожалуйста, авторизуйтесь, чтобы получить доступ к меню.")

@dp.message(F.text == "Вперед➡️")
async def display_ad(message: Message, state: FSMContext):
    check_state = await state.get_state()
    if check_state == Form.authorized.state:
        global current_ad_index
        current_ad_index += 1
        if current_ad_index >= len(ads):
            current_ad_index = 0
        ad = ads[current_ad_index]
        ad_text = (f"<b>Категория</b>: {ad[3]}\n"
                   f"<b>Местоположение</b>: {ad[4]}, {ad[5]}\n"
                   f"<b>Заголовок</b>: {ad[1]}\n"
                   f"<b>Описание</b>: {ad[2]}\n"
                   f"<b>Цена</b>: {ad[6]}")
        await message.answer(ad_text, reply_markup=ads_kb)
    else:
        await message.answer("Пожалуйста, авторизуйтесь, чтобы получить доступ к меню.")

@dp.message(F.text == "⬅️Назад")
async def display_ad(message: Message, state: FSMContext):
    check_state = await state.get_state()
    if check_state == Form.authorized.state:
        global current_ad_index
        current_ad_index -= 1
        if current_ad_index < 0:
            current_ad_index = len(ads) - 1
        ad = ads[current_ad_index]
        ad_text = (f"<b>Категория</b>: {ad[3]}\n"
                   f"<b>Местоположение</b>: {ad[4]}, {ad[5]}\n"
                   f"<b>Заголовок</b>: {ad[1]}\n"
                   f"<b>Описание</b>: {ad[2]}\n"
                   f"<b>Цена</b>: {ad[6]}")
        await message.answer(ad_text, reply_markup=ads_kb)
    else:
        await message.answer("Пожалуйста, авторизуйтесь, чтобы получить доступ к меню.")

@dp.message(F.text == "✔️Разместить объявление")
async def new_ads(message: Message, state: FSMContext):
    check_state = await state.get_state()
    if check_state == Form.authorized.state:
        await message.reply("Объявление размещается в следующем порядке:\n"
                            "1) Вводится название\n"
                            "2) Вводится описание товара\n"
                            "3) Указывается категория\n"
                            "4) Записывается город в формате: <b>Город</b> <b>Регион</b> <b>Страна</b>\n"
                            "5) Указывается цена\n")
        await message.reply("1) Введите название товара")
        await state.set_state(NewAds.title)
    else:
        await message.answer("Пожалуйста, авторизуйтесь, чтобы получить доступ к меню.")

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


# Я долбаеб, я хз как записать данные в таблицу



# Обработчик для проверки авторизации перед выполнением действий
@dp.message()
async def check_authorization(message: Message, state: FSMContext):
    current_state = await state.get_state()
    logging.info(f"Check authorization state: {current_state}")
    if current_state != Form.authorized.state:
        await message.answer("Пожалуйста, авторизуйтесь, чтобы продолжить.", reply_markup=start_kb)

# Запуск бота
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

# Закрытие соединения с базой данных
close_connection()
