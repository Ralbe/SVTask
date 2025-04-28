from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from keyboards.keyboards import filter_kb, back_kb, category_kb
from utils.states import ViewingAds
from DataBase.UserDB import get_categories

categories = get_categories()

async def show_filters(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(
        f"Фильтры установлены:\n"
        f"Категория: {data.get('category', 'не указана')}\n"
        # f"Город: {data.get('city', 'не указан')}\n"
        f"Цена от: {data.get('price_min', 'не указана')}\n"
        f"Цена до: {data.get('price_max', 'не указана')}",
        reply_markup=filter_kb
    )

async def enter_filter_mode(message: types.Message, state: FSMContext):
    await state.set_state(ViewingAds.filters)
    await show_filters(message, state)

async def filters_command(message: types.Message, state: FSMContext):
    await enter_filter_mode(message, state)

async def set_category(message: types.Message, state: FSMContext):
    await state.set_state(ViewingAds.category)
    await message.answer("Выберите категорию: ", reply_markup=await category_kb(categories))

async def process_category(message: types.Message, state: FSMContext):
    if message.text == "❌Назад":
        await enter_filter_mode(message, state)
    else:
        await state.update_data(category=message.text)
        await message.answer(f"Категория установлена: {message.text}", reply_markup=filter_kb)
        await enter_filter_mode(message, state)

async def set_price_min(message: types.Message, state: FSMContext):
    await state.set_state(ViewingAds.price_min)
    await message.answer("Введите минимальную цену:", reply_markup=types.ReplyKeyboardRemove())

async def process_price_min(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)
        await state.update_data(price_min=price)
        await message.answer(f"Минимальная цена установлена: {price}", reply_markup=filter_kb)
    except ValueError:
        await message.answer("Пожалуйста, введите число!")
    await enter_filter_mode(message, state)

async def set_price_max(message: types.Message, state: FSMContext):
    await state.set_state(ViewingAds.price_max)
    await message.answer("Введите максимальную цену:", reply_markup=types.ReplyKeyboardRemove())

async def process_price_max(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)
        await state.update_data(price_max=price)
        await message.answer(f"Максимальная цена установлена: {price}", reply_markup=filter_kb)
    except ValueError:
        await message.answer("Пожалуйста, введите число!")
    await enter_filter_mode(message, state)

async def finish_filters(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.set_data({
        "viewing_ad": data.get("viewing_ad", 0),
        "saved_ads": data.get("saved_ads", []),
        "only_saved": False,
        "author": "не указан"
    })
    await show_filters(message, state)

def register_handlers(dp):
    dp.message.register(filters_command, F.text == "⚙️Фильтры")
    dp.message.register(set_category, F.text == "📁Категория")
    dp.message.register(process_category, ViewingAds.category)
    dp.message.register(set_price_min, F.text == "💰Цена от")
    dp.message.register(process_price_min, ViewingAds.price_min)
    dp.message.register(set_price_max, F.text == "💰Цена до")
    dp.message.register(process_price_max, ViewingAds.price_max)
    dp.message.register(finish_filters, F.text == "❌Сбросить фильтры")