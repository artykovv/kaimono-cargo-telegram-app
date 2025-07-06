from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from functions.func import get_address_files

router = Router()

# Фиксированный набор допустимых callback_data (для фильтра)
VALID_NAMES = {"1688", "pinduoduo", "poizon", "taobao"}

# Создание клавиатуры из активных инструкций
async def build_instruction_kb() -> InlineKeyboardMarkup:
    instructions = await get_address_files(file_type="video")
    keyboard = [
        [InlineKeyboardButton(text=item["name"], callback_data=item["name"])]
        for item in instructions if item.get("active") and item["name"] in VALID_NAMES
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Обработка команды от пользователя
@router.message(F.text == "💬 Инструкция")
async def helper(message: Message):
    kb = await build_instruction_kb()
    await message.answer("💬 Видео инструкция по:", reply_markup=kb)

# Обработка callback по кнопке "get_instruction"
@router.callback_query(F.data == "get_instruction")
async def handle_instruction_callback(callback: CallbackQuery):
    kb = await build_instruction_kb()
    await callback.message.answer("💬 Инструкция по:", reply_markup=kb)
    await callback.answer()

# Универсальный обработчик видео-инструкций с фильтром по именам
@router.callback_query(F.data.in_(VALID_NAMES))
async def handle_instruction_video(callback: CallbackQuery):
    name = callback.data
    instructions = await get_address_files(file_type="video")
    instruction = next((item for item in instructions if item["name"] == name), None)

    if instruction and instruction.get("active"):
        await callback.message.answer_video(
            video=instruction["url"],
            caption=f"Инструкция по {instruction['name']}"
        )
    else:
        await callback.message.answer("Инструкция не найдена или отключена.")

    await callback.answer()