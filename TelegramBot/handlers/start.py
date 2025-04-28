from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from DataBase.UserDB import get_user_id_by_tg_id, get_user_data
from keyboards.keyboards import main_kb
from handlers.profile import enter_profile_mode
import logging

async def handle_menu_command(message: types.Message, state: FSMContext):
    await state.clear()
    try:
        get_user_id_by_tg_id(message.from_user.id)
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

async def handle_main_text(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите желаемый раздел.", reply_markup=main_kb)

def register_handlers(dp):
    dp.message.register(handle_menu_command, Command("start"))
    dp.message.register(handle_main_text, F.text == "🏠На главную")