
from aiogram import types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import InputMediaPhoto

from typing import List
from bot import bot
from functions.func import get_all_users_telegram_chat_ids, get_profile_user


async def handle_broadcast_text(text: str, chat_ids: list[int] = None):
    if chat_ids:
        for chat_id in chat_ids:
            try:
                await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
            except Exception as e:
                print(f"Бот заблокирован пользователем {chat_id}, сообщение не отправлено. Ошибка: {e}")
        return

    if not chat_ids:
        user_ids = await get_all_users_telegram_chat_ids()

        for user_id in user_ids:
            try:
                await bot.send_message(chat_id=user_id, text=text, parse_mode="HTML")
            except Exception as e:
                print(f"Бот заблокирован пользователем {user_id}, сообщение не отправлено. Ошибка: {e}")

async def send_photo_handle(
    photos: list[str],  # Список URL-адресов изображений
    message: str,  # Текст сообщения
    chat_ids: list[int] = None  # ID чата
):
    if not photos:
        print("Ошибка: список photos пуст!")
        return

    media = [
        InputMediaPhoto(media=photo, caption=message if i == 0 else "", parse_mode="HTML")
        for i, photo in enumerate(photos)
    ]

    if chat_ids:
        for chat_id in chat_ids:
            print(f"Отправка сообщения пользователю {chat_id}")
            try:
                await bot.send_media_group(chat_id=chat_id, media=media)
                print(f"Сообщение отправлено пользователю {chat_id}")
            except Exception as e:
                print(f"Бот заблокирован пользователем {chat_id}, сообщение не отправлено. Ошибка: {e}")

    if not chat_ids:
        user_ids = await get_all_users_telegram_chat_ids()
        for user_id in user_ids:
            try:
                await bot.send_media_group(chat_id=user_id, media=media)
                print(f"Сообщение отправлено пользователю {user_id}")
            except Exception as e:
                print(f"Бот заблокирован пользователем {user_id}, сообщение не отправлено. Ошибка: {e}")



async def send_notification_china(data: List[dict]):
    for user_data in data:
        telegram_chat_id = user_data['telegram_chat_id']
        count = user_data['count']

        
        # Получаем данные профиля пользователя
        # response = await get_profile_user(telegram_chat_id=telegram_chat_id)
        # user_data = response[0]

        # Формируем сообщение
        message = (
            f"Уведомление 🇨🇳🇨🇳🇨🇳\n\n"
            # f"Уважаемый(ая) {user_data['name']}\n"
            f"Ваши товары прибыли на склад 'Китай'\n\n"
            f"📦 Количество товаров: {count} \n\n"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Детали", callback_data="china")]
        ])

        try:
            await bot.send_message(chat_id=telegram_chat_id, text=message, reply_markup=kb)  # Используем bot для отправки сообщения
        except Exception as e:
            print(f"Бот заблокирован пользователем {telegram_chat_id}, сообщение не отправлено. Ошибка: {e}")


async def send_notification_in_transit(data: List[dict]):
    for user_data in data:
        telegram_chat_id = user_data['telegram_chat_id']
        count = user_data['count']

        
        # Получаем данные профиля пользователя
        # response = await get_profile_user(telegram_chat_id=telegram_chat_id)
        # user_data = response[0]

        # Формируем сообщение
        message = (
            f"Уведомление 🚚🚚🚚\n\n"
            # f"Уважаемый {user_data['name']}\n"
            f"Ваши товар выехали\n\n"
            f"📦 Количество товаров: {count} \n\n"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Детали", callback_data="transit")]
        ])

        try:
            await bot.send_message(chat_id=telegram_chat_id, text=message, reply_markup=kb)  # Используем bot для отправки сообщения
        except Exception as e:
            print(f"Бот заблокирован пользователем {telegram_chat_id}, сообщение не отправлено. Ошибка: {e}")

async def send_notification_bihkek(data: List[dict]):
    for user_data in data:
        telegram_chat_id = user_data['telegram_chat_id']
        count = user_data['count']

        # response = await get_profile_user(telegram_chat_id=telegram_chat_id)
        # user_data = response[0]


        # Формируем сообщение
        message = (
            f"Уведомление 🇰🇬🇰🇬🇰🇬\n\n"
            # f"Уважаемый {user_data['name']}\n"
            f"Ваши товары прибыли на склад 'Бишкек'\n\n"
            f"📦 Количество товаров: {count} \n\n"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Детали", callback_data="pickup")]
        ])


        try:
            await bot.send_message(chat_id=telegram_chat_id, text=message, reply_markup=kb)
        except Exception as e:
            print(f"Бот заблокирован пользователем {telegram_chat_id}, сообщение не отправлено. Ошибка: {e}")
