from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage


storage = MemoryStorage()

class ViewingAdsStates(StatesGroup):
    viewing_ad = State()
    
    waiting_for_category = State()
    waiting_for_city = State()
    waiting_for_price_min = State()
    waiting_for_price_max = State()


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
    waiting_for_confirm = State()
    waiting_for_change = State()
    editing_field = State()

class CheckMessage(StatesGroup):
    category_message = State()
    location_message = State()
    title_message = State()
    description_message = State()
    money_message = State()