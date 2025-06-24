from aiogram import Router, F, types
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, FSInputFile
from functions.func import get_text

router = Router()

@router.message(F.text == "❗️ Важная информация!")
async def helper(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 Запрещенные товары", callback_data="ban_products")],
        [InlineKeyboardButton(text="❗️ Важная информация", callback_data="important_info")],
    ])
    await message.answer("❗️ Важная информация!", reply_markup=kb)

@router.callback_query(F.data == "ban_products")
async def handle_instruction_callback(callback: CallbackQuery):
    ban_products = await get_text(key="banproducts")
    await callback.message.answer(text=ban_products)
    await callback.answer()

@router.callback_query(F.data == "important_info")
async def handle_instruction_callback(callback: CallbackQuery):
    important_info = await get_text(key="importantinfo")
    await callback.message.answer(text=important_info)
    await callback.answer()