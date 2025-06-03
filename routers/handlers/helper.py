from aiogram import Router, F, types
from aiogram.types import FSInputFile, InputMediaPhoto

from functions.func import get_address, get_profile_user

router = Router()


@router.message(F.text == "📕 Помощь")
async def helper(message: types.Message):
    user_id = str(message.chat.id)
    response = await get_profile_user(telegram_chat_id=user_id)
    address = await get_address()
    user_data = response[0]

    info = (
        f"Нажмите чтобы скопировать:\n\n"
        f"<code>{address['name1']}{user_data['code']}\n\n"
        f"{address['name2']}\n\n"
        f"{address['name3']}{user_data['code']}</code>"
    )

    photo_filenames = ["./images/taobao.jpg", "./images/pinduoduo.jpg", "./images/poizon.jpg", "./images/1688.jpg"]
    media_group = [InputMediaPhoto(media=FSInputFile(filename)) for filename in photo_filenames]


    await message.answer(info, parse_mode="HTML")
    await message.answer_media_group(media=media_group)
