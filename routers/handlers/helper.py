from aiogram import Router, F, types
from aiogram.types import FSInputFile, InputMediaPhoto

from functions.func import get_address, get_address_files

router = Router()


@router.message(F.text == "🇨🇳 Адрес в Китае")
async def helper(message: types.Message):
    user_id = str(message.chat.id)
    address = await get_address(telegram_chat_id=user_id)
    photos_data = await get_address_files(file_type="photo")
    active_photos = [photo for photo in photos_data if photo.get("active")]
    media_group = [
        InputMediaPhoto(media=photo["url"])
        for photo in active_photos
    ]

    await message.answer(address, parse_mode="HTML")
    await message.answer_media_group(media=media_group)
