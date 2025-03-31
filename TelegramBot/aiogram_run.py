import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from utils.stateform import Form
from DataBase.UserDB import conn, cursor
from keyboards.keyboards import main_kb


# Инициализация бота и диспетчера
API_TOKEN = '7754829803:AAF9bmNcb635GC0emlEjkd3x8_YI75IJYz4'
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == Form.authorized.state:
        await message.answer("Вы уже авторизованы.")
    else:
        await message.answer("Привет! Введите ваш email:")
        await state.set_state(Form.email)

# Обработчик состояния email
@dp.message(Form.email)
async def process_email(message: Message, state: FSMContext):
    email = message.text
    cursor.execute("SELECT * FROM people WHERE email = %s", (email,))
    user = cursor.fetchone()
    
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

    cursor.execute("SELECT * FROM people WHERE email = %s AND password = %s", (email, password))
    user = cursor.fetchone()

    if user:
        await message.answer("Вы успешно авторизованы!")
        await state.set_state(Form.authorized)  # Устанавливаем состояние авторизации
        await authorized_action(message, state)
    else:
        await message.answer("Неверный пароль. Попробуйте снова. Введите вашу почту")
        await state.set_state(Form.email)  # Возвращаемся к вводу email


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

    # Сохранение данных в базу данных
    cursor.execute("INSERT INTO people (username, password, email) VALUES (%s,%s, %s)", (login, password, email))

    await message.answer("Спасибо! Ваши данные сохранены.")
    await state.set_state(Form.authorized)  # Устанавливаем состояние авторизации
    await state.update_data(current_email=email)
    await authorized_action(message, state)


@dp.message(Command("menu"))
async def authorized_action(message: Message, state: FSMContext):
    check_state = await state.get_state()
    if check_state == Form.authorized.state:
        await message.answer("Выберите желаемый раздел.", reply_markup=main_kb)
    else:
        await message.answer("Пожалуйста, авторизуйтесь, чтобы получить доступ к меню.")


@dp.message(F.text == "🚪Выйти с аккаунта")
async def exit(message: Message, state:FSMContext):
    check_state = await state.get_state()
    if check_state == Form.authorized.state:
        #Получаем название почты
        user_data = await state.get_data()
        email = user_data.get('current_email')
        await message.answer(f"Вы вышли из аккаунта {email}")
        await state.clear()
    else:
        await message.answer("Пожалуйста, авторизуйтесь, чтобы получить доступ к меню.")


# Обработчик для проверки авторизации перед выполнением действий
@dp.message()
async def check_authorization(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state != Form.authorized.state:
        await message.answer("Пожалуйста, авторизуйтесь, чтобы продолжить.")


# Запуск бота
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

# Закрытие соединения с базой данных
cursor.close()
conn.close()
