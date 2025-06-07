from aiogram import Router, F, types
from aiogram.types import FSInputFile, InputMediaPhoto

from functions.func import get_address, get_profile_user

router = Router()


@router.message(F.text == "📕 Помощь")
async def helper(message: types.Message):
    user_id = str(message.chat.id)
    address = await get_address(telegram_chat_id=user_id)
    photo_filenames = ["./images/taobao.jpg", "./images/pinduoduo.jpg", "./images/poizon.jpg", "./images/1688.jpg"]
    media_group = [InputMediaPhoto(media=FSInputFile(filename)) for filename in photo_filenames]


    await message.answer(address, parse_mode="HTML")
    await message.answer_media_group(media=media_group)
