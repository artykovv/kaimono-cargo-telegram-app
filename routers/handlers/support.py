from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text == "⚙️ Поддержка")
async def main_products(message: Message):
    info = (
        f"Позвоните по этому номеру для помощи:\n\n"
        f"+996501870037"
    )
    await message.answer(info)