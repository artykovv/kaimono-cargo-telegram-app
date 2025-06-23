from aiogram import Router, types, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from functions.func import get_profile_user
from conf.config import REGISTER_SITE_URL

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
        f"📞 Адрес: {user_data['number']}\n\n"

        f"🪪 Код: KBK{user_data['numeric_code']}\n"
    )

    update_button = InlineKeyboardButton(
            text="Изменить",
            web_app=WebAppInfo(url=f"{REGISTER_SITE_URL}/update")  # укажи свой URL
        )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[update_button]])
    
    await message.answer(text=user_info, reply_markup=keyboard)