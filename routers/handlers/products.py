from aiogram import Router, types, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

@router.message(F.text == "📥 Мои товары")
async def main_products(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Можно забрать", callback_data="pickup")],
        [InlineKeyboardButton(text="🚚 В пути", callback_data="transit")],
        [InlineKeyboardButton(text="🇨🇳 В китае", callback_data="china")]
    ])
    await message.answer("Выберите:", reply_markup=kb)