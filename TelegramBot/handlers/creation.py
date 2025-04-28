from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto, ReplyKeyboardMarkup, KeyboardButton
from keyboards.keyboards import confirm_kb, red_kb, back_kb,main_kb ,category_kb
from utils.states import NewAds
from DataBase.UserDB import (
    get_categories, insert_new_ad, get_category_id, add_category,
    update_ad, delete_ad_photos, add_photo, get_ad_by_id,get_user_id_by_tg_id
)
import logging

categories = get_categories()

async def new_ads(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(NewAds.title)
    await state.update_data({"changing_ad": False})
    await message.reply("Введите название товара")

async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.reply("Введите описание товара")
    await state.set_state(NewAds.description)

async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.reply("Выберете категорию товара", reply_markup=await category_kb(categories))
    await state.set_state(NewAds.category)

async def process_category(message: types.Message, state: FSMContext):
    if (message.text,) in categories:
        await state.update_data(category=message.text)
        await message.reply("Укажите стоимость")
        await state.set_state(NewAds.money)
    elif message.text == "❌Назад":
        from handlers.ads import show_ads
        await show_ads(message, state)
    else:
        await message.reply("Выберете категорию товара", reply_markup=await category_kb(categories))
        await state.set_state(NewAds.category)

async def process_money(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)
        await state.update_data(money=price)
        await message.answer(
            "Теперь пришлите фотографии товара (до 10 штук). Когда закончите, нажмите 'Готово'",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Готово")]],
                resize_keyboard=True
            ))
        await state.update_data(photos=[])
        await state.set_state(NewAds.photos)
    except ValueError:
        await message.reply("Пожалуйста, введите число!")

async def process_photo(message: types.Message, state: FSMContext):
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

async def finish_photos(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    
    if not photos:
        await message.answer(
            "Вы не добавили ни одного фото. Хотите продолжить без фото?",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Да"), KeyboardButton(text="Добавить фото")]
                ],
                resize_keyboard=True
            ))
        return
    
    await show_ad_preview(message, state)

async def show_ad_preview(message: types.Message, state: FSMContext):
    data = await state.get_data()
    ad_text = (
        f"<b>Заголовок</b>: {data['title']}\n"
        f"<b>Описание</b>: {data['description']}\n"
        f"<b>Категория</b>: {data['category']}\n"
        f"<b>Цена</b>: {data['money']}"
    )
    
    photos = data.get("photos", [])
    
    if photos:
        media = [InputMediaPhoto(media=photos[0], caption=ad_text)]
        media.extend([InputMediaPhoto(media=photo) for photo in photos[1:]])
        await message.answer_media_group(media=media)
        await message.answer("Ваше объявление будет выглядеть так:", reply_markup=confirm_kb)
    else:
        await message.answer("Ваше объявление будет выглядеть так:\n\n" + ad_text, reply_markup=confirm_kb)
    
    await state.set_state(NewAds.confirm)

async def message_okey(message: types.Message, state: FSMContext):
    if message.text == "✅Разместить":
        try:
            data = await state.get_data()
            tg_id = message.from_user.id
            category = data["category"]
            title = data["title"]
            description = data["description"]
            money = data["money"]
            photos = data.get("photos", [])

            user_id = await get_user_id_by_tg_id(tg_id)
            category_id = await get_category_id(category)
            if not category_id:
                category_id = await add_category(category)

            if data["changing_ad"]:
                ad_id = data["ad_id"]
                await update_ad(ad_id, user_id, category_id, title, description, money)
                await delete_ad_photos(ad_id)
            else:
                ad_id = await insert_new_ad(user_id, category_id, title, description, money)

            for photo in photos:
                try:
                    await add_photo(ad_id, photo)
                except Exception as e:
                    logging.error(f"Ошибка при сохранении фото: {e}")
                    continue

            await message.reply("✅ Ваше объявление размещено", reply_markup=main_kb)
            await state.clear()
            from handlers.start import handle_main_text
            await handle_main_text(message, state)
        except Exception as e:
            logging.error(f"Error publishing ad: {e}")
            await message.answer("❌ Ошибка при размещении объявления. Попробуйте позже.")

async def edit_photos(message: types.Message, state: FSMContext):
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

async def add_more_photos(message: types.Message, state: FSMContext):
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

async def process_additional_photo(message: types.Message, state: FSMContext):
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

async def finish_additional_photos(message: types.Message, state: FSMContext):
    await show_ad_preview(message, state)

async def remove_all_photos(message: types.Message, state: FSMContext):
    await state.update_data(photos=[])
    await message.answer("Все фото удалены.", reply_markup=red_kb)
    await state.set_state(NewAds.change)

async def select_field_to_edit(message: types.Message, state: FSMContext):
    field_map = {
        "Заголовок": "title",
        "Описание": "description",
        "Категория": "category",
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
        "money": "Введите новую цену:"
    }
    await message.answer(prompts[field_name], reply_markup=back_kb if field_name != 'category' else await category_kb(categories))
    await state.set_state(NewAds.editing_field)

async def process_field_edit(message: types.Message, state: FSMContext):
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
        f"<b>Цена</b>: {data['money']}"
    )
    await message.answer("Изменения сохранены. Ваше объявление:\n\n" + ad_text, reply_markup=confirm_kb)

def register_handlers(dp):
    dp.message.register(new_ads, F.text == "✔️Разместить объявление")
    dp.message.register(process_title, NewAds.title)
    dp.message.register(process_description, NewAds.description)
    dp.message.register(process_category, NewAds.category)
    dp.message.register(process_money, NewAds.money)
    dp.message.register(process_photo, NewAds.photos, F.photo)
    dp.message.register(finish_photos, NewAds.photos, F.text == "Готово")
    dp.message.register(message_okey, NewAds.confirm)
    dp.message.register(edit_photos, NewAds.change, F.text == "Фотографии")
    dp.message.register(add_more_photos, NewAds.edit_photos, F.text == "Добавить фото")
    dp.message.register(process_additional_photo, NewAds.add_more_photos, F.photo)
    dp.message.register(finish_additional_photos, NewAds.add_more_photos, F.text == "Готово")
    dp.message.register(remove_all_photos, NewAds.edit_photos, F.text == "Удалить все фото")
    dp.message.register(select_field_to_edit, NewAds.change)
    dp.message.register(process_field_edit, NewAds.editing_field)