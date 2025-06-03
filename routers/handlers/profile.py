from aiogram import Router, types, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from functions.func import get_profile_user

router = Router()

@router.message(F.text == "👤 Профиль")
async def main_products(message: Message):
    user_id = str(message.chat.id)
    response = await get_profile_user(telegram_chat_id=user_id)
    user_data = response[0]
    user_info = (
        f"📃 Профиль 📃 \n\n"
        f"👤 ФИО: {user_data['name']}\n"
        f"🌍 Город: {user_data['city']}\n"
        f"📞 Номер: {user_data['number']}\n\n"

        f"🪪 Код: {user_data['code']}\n"
    )
    await message.answer(user_info)