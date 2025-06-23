from aiogram import Router, F, types
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, FSInputFile
router = Router()


@router.message(F.text == "💬 Инструкция")
async def helper(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1688", callback_data="1688")],
        [InlineKeyboardButton(text="pinduoduo", callback_data="pinduoduo")],
        [InlineKeyboardButton(text="poizon", callback_data="poizon")],
        [InlineKeyboardButton(text="taobao", callback_data="taobao")]
    ])
    await message.answer("💬 Инструкция по:", reply_markup=kb)

@router.callback_query(F.data == "1688")
async def search_product(callback: CallbackQuery):
    video = FSInputFile("video/1688.mp4")
    await callback.message.answer_video(video=video, caption="Инструкция по 1688")
    await callback.answer()

@router.callback_query(F.data == "pinduoduo")
async def search_product(callback: CallbackQuery):
    video = FSInputFile("video/pinduoduo.mp4")
    await callback.message.answer_video(video=video, caption="Инструкция по pinduoduo")
    await callback.answer()

@router.callback_query(F.data == "poizon")
async def search_product(callback: CallbackQuery):
    video = FSInputFile("video/poizon.mp4")
    await callback.message.answer_video(video=video, caption="Инструкция по poizon")
    await callback.answer()

@router.callback_query(F.data == "taobao")
async def search_product(callback: CallbackQuery):
    video = FSInputFile("video/taobao.mp4")
    await callback.message.answer_video(video=video, caption="Инструкция по taobao")
    await callback.answer()