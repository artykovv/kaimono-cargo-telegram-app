from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(F.text.in_(["Назад в главное меню", "Вернуться в меню", "Главное меню"]))
@router.message(Command("menu"))
async def main_to_menu(message: Message):
    kb = [
        [types.KeyboardButton(text="📥 Мои товары")],
        [
            types.KeyboardButton(text="🔎 Поиск"),
            types.KeyboardButton(text="👤 Профиль")
        ],
        [
            types.KeyboardButton(text="⚙️ Поддержка"),
            types.KeyboardButton(text="📕 Помощь"),
            types.KeyboardButton(text="📬 Адреса"),
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            input_field_placeholder="Выберите"
        )
    await message.answer("Главное меню", reply_markup=keyboard)


@router.message(Command("my"))
async def my_chat_id(message: Message):
    await message.answer(f"Ваш chat_id: {message.chat.id}")