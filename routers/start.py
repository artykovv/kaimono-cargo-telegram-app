from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from functions.func import validate_user_telegram_chat_id

router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    user_id = str(message.chat.id)
    user = await validate_user_telegram_chat_id(telegram_chat_id=user_id)
    if user:
        kb = [[types.KeyboardButton(text="Главное меню")]]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            input_field_placeholder="Выберите"
        )
        info = (
            f"Вас приветствует транспортная компания Kaimono Cargo 🤝\n"
            f"У нас самая быстрая доставка по Кыргызстану, от 6-12 дней 🚛\n"
            f"2,5$ за кг🔥\n"
            f"С нами быстро и надежно 💯\n\n"
            f"👋 Вы уже зарегистрированы\n\n"
           
        )
        await message.answer(info, reply_markup=keyboard)
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Регистрация", callback_data="register_user")],
        ])

        info = (
            f"Вас приветствует транспортная компания Kaimono Cargo 🤝\n"
            f"У нас самая быстрая доставка по Кыргызстану, от 6-12 дней 🚛\n"
            f"2,5$ за кг🔥\n"
            f"С нами быстро и надежно 💯\n\n"
            f"Вы не зарегистрированы. Пожалуйста нажмите регистрация, для использования бота\n\n"
        )
        await message.answer(info, reply_markup=kb)



    
