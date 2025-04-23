from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage


storage = MemoryStorage()

class ViewingAds(StatesGroup):
    ads = State()
    viewing_ad = State()
    filters = State()
    category = State()
    city = State()
    price_min = State()
    price_max = State()
    saved_ads = State()

class ProfileStates(StatesGroup):
    waiting_for_field = State()

class Profile(StatesGroup):
    first_name = State()
    second_name = State()
    phone = State()
    email = State()


class Form(StatesGroup):
    email = State()
    login = State()
    password = State()
    auth_password = State()  # Состояние для ввода пароля при авторизации
    authorized = State()  # Состояние для авторизованного пользователя

# class Form(StatesGroup):
#     name = State()
#     number = State()
#     auth_password = State()  # Состояние для ввода пароля при авторизации
#     authorized = State()  # Состояние для авторизованного пользователя


class NewAds(StatesGroup):
    category = State()
    location = State()
    title = State()
    description = State()
    money = State()
    confirm = State()
    change = State()
    editing_field = State()

class CheckMessage(StatesGroup):
    category_message = State()
    location_message = State()
    title_message = State()
    description_message = State()
    money_message = State()