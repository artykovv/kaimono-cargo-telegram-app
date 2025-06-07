from aiogram import Router, F
from aiogram.types import Message, InputMediaPhoto, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from functions.func import get_profile_user, get_address, get_branches, update_branch 

router = Router()

# Обработчик команды "📬 Адреса"
@router.message(F.text == "📬 Адреса")
async def address(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Поменять филиал", callback_data="address_bishkek")],
        [InlineKeyboardButton(text="Китай адрес", callback_data="address_china")],
    ])
    await message.answer("Выберите:", reply_markup=kb)


@router.callback_query(F.data == "address_china")
async def china_address(callback: CallbackQuery):
    user_id = str(callback.message.chat.id)
    address = await get_address(telegram_chat_id=user_id)
    photo_filenames = ["./images/taobao.jpg", "./images/pinduoduo.jpg", "./images/poizon.jpg", "./images/1688.jpg"]
    media_group = [InputMediaPhoto(media=FSInputFile(filename)) for filename in photo_filenames]

    await callback.message.edit_text(address, parse_mode="HTML")
    await callback.message.answer_media_group(media=media_group)


# Обработчик выбора "Бишкек филиалы"
@router.callback_query(F.data == "address_bishkek")
async def address_bishkek(callback: CallbackQuery):
    branches = await get_branches()
    if not branches:
        await callback.message.edit_text("Не удалось загрузить список филиалов.")
        return

    # Формируем кнопки с филиалами
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{branch['name']} ({branch['address']})",
                    callback_data=f"select_branch_{branch['id']}"
                )
            ]
            for branch in branches
        ]
    )
    await callback.message.edit_text("Выберите филиал:", reply_markup=keyboard)

# Обработчик выбора конкретного филиала
@router.callback_query(F.data.startswith("select_branch_"))
async def confirm_branch_change(callback: CallbackQuery):
    branch_id = int(callback.data.split("_")[-1])  # Извлекаем branch_id
    telegram_chat_id = str(callback.message.chat.id)  # telegram_chat_id

    # Находим информацию о филиале
    branches = await get_branches()
    selected_branch = next((b for b in branches if b["id"] == branch_id), None)
    if not selected_branch:
        await callback.message.edit_text("Филиал не найден.")
        return

    # Формируем сообщение с подтверждением
    confirmation_text = (
        f"Вы уверены, что хотите сменить филиал на {selected_branch['name']} ({selected_branch['address']})?\n"
        "Ваш клиентский код изменится, и соответственно адрес на складе тоже обновится."
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да", callback_data=f"confirm_branch_{branch_id}"),
                InlineKeyboardButton(text="Нет", callback_data="cancel_branch_change")
            ]
        ]
    )
    await callback.message.edit_text(confirmation_text, reply_markup=keyboard)

# Обработчик подтверждения "Да"
@router.callback_query(F.data.startswith("confirm_branch_"))
async def process_branch_change(callback: CallbackQuery):
    branch_id = int(callback.data.split("_")[-1])
    telegram_chat_id = str(callback.message.chat.id)
    response = await update_branch(telegram_chat_id, branch_id)
    if response.status_code == 200:
        await callback.message.edit_text("Филиал успешно обновлён!")
        await show_china_address(telegram_chat_id, callback.message)
    else:
        await callback.message.edit_text(
            f"Ошибка при обновлении филиала: {response.status_code} - {response.text}"
        )

# Обработчик отмены "Нет"
@router.callback_query(F.data == "cancel_branch_change")
async def cancel_branch_change(callback: CallbackQuery):
    await callback.message.edit_text("Смена филиала отменена. Выберите другой филиал или используйте меню.")    

# Функция для показа адреса Китая
async def show_china_address(chat_id: str, message: Message):
    address = await get_address(telegram_chat_id=chat_id)
    photo_filenames = ["./images/taobao.jpg", "./images/pinduoduo.jpg", "./images/poizon.jpg", "./images/1688.jpg"]
    media_group = [InputMediaPhoto(media=FSInputFile(filename)) for filename in photo_filenames]

    await message.answer(address, parse_mode="HTML")
    await message.answer_media_group(media=media_group)