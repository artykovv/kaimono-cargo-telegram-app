from aiogram import Router, F
from aiogram.types import Message
from functions.func import get_text

router = Router()

@router.message(F.text == "⚙️ Поддержка")
async def main_products(message: Message):
    text = await get_text(key="supprot")
    await message.answer(text)