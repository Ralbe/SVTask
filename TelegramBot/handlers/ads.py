from aiogram import F, Bot, Dispatcher
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto, CallbackQuery
from DataBase.UserDB import (
    get_ads, get_saved_by_user, get_user_ads, get_ad_photos,
    increment_ad_views, get_statistic, get_contact_by_ad_id,
    get_ad_by_id, remove_ad_from_saved, add_ad_in_saved, 
    get_user_id_by_tg_id
)
from keyboards.keyboards import ads_ikb, ads_kb_showed, ads_kb_hided, confirm_kb
from utils.states import ViewingAds, NewAds
from utils.formatters import format_date
import logging

async def show_ads(message: Message, state: FSMContext):
    await state.update_data(
        viewing_ad=0,
        author='не указан',
        only_saved=False,
        saved_ads=get_saved_by_user(get_user_id_by_tg_id(message.from_user.id)),
        ad_msg_id =0,
        stat_msg_id = 0,
        showed_kb = True,
        user_id = get_user_id_by_tg_id(message.from_user.id)
    )
    await state.set_state(ViewingAds.viewing_ad)
    await display_current_ad(message, state)


async def check_ad_filters(ad: tuple, filters: dict, state: FSMContext) -> bool:
    ad_id, ad_author, _, _, ad_category, ad_city, ad_price, ad_create_date = ad
    data = await state.get_data()
    liked_list = data.get("saved_ads", [])
    only_saved = data.get("only_saved", False)

    if only_saved and (ad_id,) not in liked_list:
        return False
    if filters['author'] != 'не указан' and ad_author != filters['author']:
        return False
    if filters['category'] != 'не указана' and ad_category != filters['category']:
        return False
    if filters['city'] != 'не указан' and ad_city != filters['city']:
        return False
    if filters['price_min'] != 'не указана' and ad_price < int(filters['price_min']):
        return False
    if filters['price_max'] != 'не указана' and ad_price > int(filters['price_max']):
        return False
    return True


async def find_next_filtered_ad(current_index: int, filters: dict, state: FSMContext, forward: bool = True) -> int:
    ads = get_ads()
    if not ads:
        return -1
    step = 1 if forward else -1
    checked = 0
    total_ads = len(ads)
    while checked < total_ads:
        current_index = (current_index + step) % total_ads
        if current_index < 0:
            current_index = total_ads - 1
        if await check_ad_filters(ads[current_index], filters, state):
            return current_index
        checked += 1
    return current_index


async def display_current_ad(message: Message, state: FSMContext):
    print()
    try:
        ads = get_ads()
    except Exception as e:
        logging.error(f"Failed to fetch ads: {e}")
        await message.answer("Ошибка при загрузке объявлений.")
        return

    data = await state.get_data()
    current_index = data.get("viewing_ad", 0)
    ad = ads[current_index]
    ad_id = ad[0]
    
    # Получаем фото для объявления
    photos = get_ad_photos(ad_id)
    
    ad_text = (
        f"<b>Категория</b>: {ad[4]}\n"
        f"<b>Местоположение</b>: {ad[5]}\n"
        f"<b>Заголовок</b>: {ad[2]}\n"
        f"<b>Описание</b>: {ad[3]}\n"
        f"<b>Цена</b>: {ad[6]}"
    )

    # Проверяем, является ли объявление пользовательским
    user_id = data.get('user_id')
    user_ads = get_user_ads(user_id) or []
    your_ad = (ad_id,) in user_ads
    
    if not your_ad:
        increment_ad_views(ad_id)

    liked_ad = (ad_id,) in data.get("saved_ads", [])
    
    stats = get_statistic((ad_id,))
    if stats is None:
        stats = (0, 0)  # Значения по умолчанию

    stats_text = (
        f"📊 <b>Статистика объявления</b>:\n"
        f"📅 Дата создания объявления: {await format_date(ad[7])}\n"
        f"👁 Просмотры: {stats[0]}\n"
        f"❤️ Сохранения: {stats[1]}\n"
    )
    
    # try:
        # if photos:
        #     # Отправляем фото с подписью
        #     media = [InputMediaPhoto(media=photos[0], caption=ad_text)]
        #     # Добавляем остальные фото
        #     media.extend([InputMediaPhoto(media=photo) for photo in photos[1:]])
            
        #     # Удаляем старые сообщения если они есть
        #     if data.get("ad_msg_id"):
        #         await bot.delete_message(chat_id=message.chat.id, message_id=data.get("ad_msg_id"))
        #     if data.get("photo_group_id"):
        #         await bot.delete_message(chat_id=message.chat.id, message_id=data.get("photo_group_id"))
        #     if data.get("stat_msg_id"):
        #         await bot.delete_message(chat_id=message.chat.id, message_id=data.get("stat_msg_id"))
            
        #     # Отправляем группу фото
        #     sent_messages = await bot.send_media_group(chat_id=message.chat.id, media=media)
        #     photo_group_id = sent_messages[0].message_id
            
        #     # Отправляем статистику и кнопки
        #     stat_msg = await message.answer(stats_text, reply_markup=ads_kb_showed if data.get("showed_kb") else ads_kb_hided)
        #     buttons_msg = await message.answer("Действия:", reply_markup=ads_ikb(liked_ad, your_ad))
            
        #     await state.update_data(
        #         photo_group_id=photo_group_id,
        #         stat_msg_id=stat_msg.message_id,
        #         ad_msg_id=buttons_msg.message_id
        #     )
        # else:
        #     # Старая логика для объявлений без фото
        #     await bot.edit_message_text(text=stats_text, chat_id=message.chat.id, 
        #                               message_id=data.get("stat_msg_id"),
        #                               reply_markup=ads_kb_showed if data.get("showed_kb") else ads_kb_hided)
        #     await bot.edit_message_text(text=ad_text, chat_id=message.chat.id, 
        #                               message_id=data.get("ad_msg_id"),
        #                               reply_markup=ads_ikb(liked_ad, your_ad))
    # except Exception as e:
        # logging.error(f"Failed to change ad text: {e}")
        # Удаляем старые сообщения если они есть
    if data.get("ad_msg_id"):
        await bot.delete_message(chat_id=message.chat.id, message_id=data.get("ad_msg_id"))
    if data.get("stat_msg_id"):
        await bot.delete_message(chat_id=message.chat.id, message_id=data.get("stat_msg_id"))
    if data.get("photo_group_id"):
        await bot.delete_message(chat_id=message.chat.id, message_id=data.get("photo_group_id"))
    
    if photos:
        media = [InputMediaPhoto(media=photos[0], caption=ad_text)]
        media.extend([InputMediaPhoto(media=photo) for photo in photos[1:]])
        sent_messages = await bot.send_media_group(chat_id=message.chat.id, media=media)
        photo_group_id = sent_messages[0].message_id
        buttons_msg = await message.answer("Действия:", reply_markup=ads_ikb(liked_ad, your_ad))
        stat_msg = await message.answer(stats_text, reply_markup=ads_kb_showed if data.get("showed_kb") else ads_kb_hided)
        
        await state.update_data(
            photo_group_id=photo_group_id,
            stat_msg_id=stat_msg.message_id,
            ad_msg_id=buttons_msg.message_id
        )
    else:
        ad_msg = await message.answer(ad_text, reply_markup=ads_ikb(liked_ad, your_ad))    
        stat_msg = await message.answer(stats_text, reply_markup=ads_kb_showed if data.get("showed_kb") else ads_kb_hided)
        await state.update_data(
            ad_msg_id=ad_msg.message_id, 
            stat_msg_id=stat_msg.message_id,
            photo_group_id=None
        )


async def next_ad(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    current_index = data.get("viewing_ad", 0)
    filters = {
        'category': data.get('category', 'не указана'),
        'city': data.get('city', 'не указан'),
        'price_min': data.get('price_min', 'не указана'),
        'price_max': data.get('price_max', 'не указана'),
        'author': data.get('author', 'не указан')
    }
    new_index = await find_next_filtered_ad(current_index, filters, state, forward=True)
    await state.update_data(viewing_ad=new_index)
    await display_current_ad(callback.message, state)
    # await callback.message.delete()
    # await bot.delete_message(chat_id=callback.message.chat.id,
    #                     message_id=callback.message.message_id+1)
    
    # await state.update_data(ad_msg_id = callback.message.message_id, stat_msg_id = callback.message.message_id+1)


async def prev_ad(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    current_index = data.get("viewing_ad", 0)
    filters = {
        'category': data.get('category', 'не указана'),
        'city': data.get('city', 'не указан'),
        'price_min': data.get('price_min', 'не указана'),
        'price_max': data.get('price_max', 'не указана'),
        'author': data.get('author', 'не указан')
    }
    new_index = await find_next_filtered_ad(current_index, filters, state, forward=False)
    await state.update_data(viewing_ad=new_index)
    # await callback.message.delete()
    # await bot.delete_message(chat_id=callback.message.chat.id,
    #                     message_id=callback.message.message_id+1)

    # await state.update_data(ad_msg_id = callback.message.message_id, stat_msg_id = callback.message.message_id+1)
    await display_current_ad(callback.message, state)


async def get_contact(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    ad_id = data.get("ad_id")
    author_data = get_contact_by_ad_id(ad_id)

    # print("\n\n\n",ad_id)
    # print(author_data, "\n\n\n")
    try:
        author_name = author_data[0][0]
        author_tg_id = author_data[0][1]
    except Exception as e:
        await callback.message.answer("Ошибка, попробуйте позже")
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text=f"Вот ссылка на пользователя: {f'[{author_name}](tg://user?id={author_tg_id})'}",
        parse_mode="MarkdownV2"
        )
    # await callback.message.answer(f"Вот ссылка на пользователя: {f'[{author_name}](tg://user?id={author_tg_id} )'}")


async def change_ad(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    ad_id = data.get("ad_id")
    ad_data = get_ad_by_id(ad_id)[0]
    
    # Получаем текущие фото объявления
    photos = get_ad_photos(ad_id)
    
    await state.update_data({
        "ad_id": ad_data[0],
        "title": ad_data[1],
        "description": ad_data[2],
        "category": ad_data[3],
        "money": ad_data[5],
        "photos": photos,  # Сохраняем текущие фото
        "changing_ad": True
    })
    
    await show_ad_preview(callback.message, state)
    await state.set_state(NewAds.confirm)


async def handle_saved_actions(callback: CallbackQuery, state: FSMContext):
    try:
        # 1. Получаем данные
        user_id = get_user_id_by_tg_id(callback.from_user.id)
        if not user_id:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return

        data = await state.get_data()
        ad_id = data.get("ad_id")
        if not ad_id:
            await callback.answer("❌ Объявление не найдено", show_alert=True)
            return

        # 2. Выполняем действие
        if callback.data == "remove_from_saved":
            remove_ad_from_saved(ad_id, user_id)
            liked_ad = False
        else:
            add_ad_in_saved(ad_id, user_id)
            liked_ad = True

        # 3. Обновляем состояние
        try:
            saved_ads = get_saved_by_user(user_id) or []
            await state.update_data(saved_ads=saved_ads)
        except Exception as e:
            logging.error(f"Ошибка обновления состояния: {e}")

        # 4. Обновляем интерфейс
        your_ad = (ad_id,) in (get_user_ads(user_id) or [])
        try:
            stats = get_statistic((ad_id))
            data = await state.get_data()
            ad = get_ad_by_id(ad_id)
            stats_text = (
                f"📊 <b>Статистика объявления</b>:\n"
                f"📅 Дата создания объявления: {await format_date(ad[6])}\n"
                f"👁 Просмотры: {stats[0]}\n"
                f"❤️ Сохранения: {stats[1]}\n"
                # f"📞 Запросы контактов: {stats[2]}"
    )
            # await bot.edit_message_text(text = stats_text, chat_id=callback.message.chat.id, message_id = callback.message.message_id+1,
            #                             reply_markup = ads_kb_showed if data.get("showed_kb") else ads_kb_hided)
            # await bot.edit_message_reply_markup(message_id=callback.message.message_id+1, reply_markup = ads_kb_showed if data.get("showed_kb") else ads_kb_hided)
            await callback.message.edit_reply_markup(
                reply_markup=ads_ikb(liked_ad, your_ad)
            )
        except Exception as e:
            logging.error(f"Ошибка обновления интерфейса: {e}")
            # await callback.answer("✅ Обновлено")
            
        await display_current_ad(callback.message, state)

    except Exception as e:
        logging.error(f"Ошибка в обработке избранного: {e}")
        await callback.answer("❌ Ошибка при обработке запроса", show_alert=True)


async def show_own_ads(message: Message, state: FSMContext):
    await state.update_data(
        viewing_ad=0,
        saved_ads=get_saved_by_user(get_user_id_by_tg_id(message.from_user.id)),
        author=get_user_id_by_tg_id(message.from_user.id),
        only_saved=False
    )
    await state.set_state(ViewingAds.viewing_ad)
    data = await state.get_data()
    filters = {
        'category': data.get('category', 'не указана'),
        'city': data.get('city', 'не указан'),
        'price_min': data.get('price_min', 'не указана'),
        'price_max': data.get('price_max', 'не указана'),
        'author': get_user_id_by_tg_id(message.from_user.id)
    }

    print()
    new_index = await find_next_filtered_ad(0, filters, state, forward=True)
    await state.update_data(viewing_ad=new_index)
    await display_current_ad(message, state)

async def show_saved_ads(message: Message, state: FSMContext):
    await state.update_data(
        viewing_ad=0,
        saved_ads=get_saved_by_user(get_user_id_by_tg_id(message.from_user.id)),
        only_saved=True,
        author="не указан"
    )
    await state.set_state(ViewingAds.viewing_ad)
    await display_current_ad(message, state)

async def show_ad_preview(message: Message, state: FSMContext):
    data = await state.get_data()
    ad_text = (
        f"<b>Заголовок</b>: {data['title']}\n"
        f"<b>Описание</b>: {data['description']}\n"
        f"<b>Категория</b>: {data['category']}\n"
        f"<b>Цена</b>: {data['money']}"
    )
    
    photos = data.get("photos", [])
    
    if photos:
        # Отправляем первое фото с подписью и кнопками
        media = [InputMediaPhoto(media=photos[0], caption=ad_text)]
        # Добавляем остальные фото без подписи
        media.extend([InputMediaPhoto(media=photo) for photo in photos[1:]])
        
        await message.answer_media_group(media=media)
        await message.answer("Ваше объявление будет выглядеть так:", reply_markup=confirm_kb)
    else:
        await message.answer("Ваше объявление будет выглядеть так:\n\n" + ad_text, reply_markup=confirm_kb)
    
    await state.set_state(NewAds.confirm)

async def show_menu_kb(message: Message, state: FSMContext):
    await state.update_data(showed_kb = True)
    await message.answer("Меню показано", reply_markup = ads_kb_showed)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

async def hide_menu_kb(message: Message, state: FSMContext):
    await state.update_data(showed_kb = False)
    await message.answer("Меню скрыто", reply_markup = ads_kb_hided)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

def register_handlers(dp: Dispatcher, _bot: Bot):
    global bot
    bot = _bot
    dp.message.register(show_ads, F.text == "🕶Объявления")
    dp.callback_query.register(next_ad, F.data == "next_ad")
    dp.callback_query.register(prev_ad, F.data == "prev_ad")
    dp.callback_query.register(get_contact, F.data == "get_contact")
    dp.callback_query.register(change_ad, F.data == "change_ad")
    dp.callback_query.register(handle_saved_actions, F.data.in_(["remove_from_saved", "add_in_saved"]))
    dp.message.register(show_own_ads, F.text == "Мои объявления")
    dp.message.register(show_saved_ads, F.text == "Сохраненные объявления")
    dp.message.register(show_menu_kb, F.text == "⬆️Показать меню")
    dp.message.register(hide_menu_kb, F.text == "⬇️Скрыть меню")