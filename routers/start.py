from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from conf.config import REGISTER_SITE_URL
from functions.func import get_text, validate_user_telegram_chat_id

router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    user_id = str(message.chat.id)
    user = await validate_user_telegram_chat_id(telegram_chat_id=user_id)

    text = await get_text(key="welcome")

    if user:
        kb = [[types.KeyboardButton(text="Главное меню")]]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            input_field_placeholder="Выберите"
        )
        info = (
            f"{text}\n\n"
            f"👋 Вы уже зарегистрированы\n\n"
        )
        await message.answer(info, reply_markup=keyboard, parse_mode="HTML")

    else:
        register_button = InlineKeyboardButton(
            text="Регистрация",
            web_app=WebAppInfo(url=f"{REGISTER_SITE_URL}/register")  # укажи свой URL
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[[register_button]])

        info = (
            f"{text}\n\n"
            f"Вы не зарегистрированы. Пожалуйста нажмите «Регистрация», чтобы продолжить\n\n"
        )
        await message.answer(info, reply_markup=keyboard, parse_mode="HTML")