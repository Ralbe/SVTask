from aiogram.fsm.state import StatesGroup, State

class NewAds(StatesGroup):
    title = State()
    description = State()
    category = State()
    money = State()
    photos = State()
    confirm = State()
    change = State()
    editing_field = State()
    edit_photos = State()
    add_more_photos = State()

class CheckMessage(StatesGroup):
    waiting_for_message = State()

class ViewingAds(StatesGroup):
    viewing_ad = State()
    filters = State()
    category = State()
    city = State()
    price_min = State()
    price_max = State()

class ProfileStates(StatesGroup):
    waiting_for_field = State()

class Profile(StatesGroup):
    waiting_for_data = State()