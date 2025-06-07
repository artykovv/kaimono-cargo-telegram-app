# from aiogram import Router, F, types
# from aiogram.fsm.state import State, StatesGroup
# from aiogram.fsm.context import FSMContext
# from aiogram.types import (
#     CallbackQuery, 
#     InlineKeyboardButton, 
#     InlineKeyboardMarkup, 
#     InputMediaPhoto, 
#     FSInputFile
# )

# from functions.func import get_branches, post_request_register, get_address

# router = Router()


# class GetService(StatesGroup):
#     name = State()
#     number = State()
#     city = State()
#     branch = State()

# @router.callback_query(F.data == "register_user")
# async def register_user(callback: CallbackQuery, state: FSMContext):
#     """Начало регистрации: запрашиваем имя."""
#     await callback.message.edit_text("Введите ваше имя:")
#     await state.set_state(GetService.name)

# @router.message(GetService.name)
# async def get_name(message: types.Message, state: FSMContext):
#     """Сохраняем имя, запрашиваем номер телефона."""
#     await state.update_data(name=message.text)
#     await message.answer("Введите ваш номер телефона:")
#     await state.set_state(GetService.number)

# @router.message(GetService.number)
# async def get_number(message: types.Message, state: FSMContext):
#     """Сохраняем номер, запрашиваем город."""
#     await state.update_data(number=message.text)
#     await message.answer("Введите ваш адрес:")
#     await state.set_state(GetService.city)

# @router.message(GetService.city)
# async def get_city(message: types.Message, state: FSMContext):
#     """После ввода города выводим список филиалов в виде инлайн-кнопок."""
#     await state.update_data(city=message.text)

#     branches = await get_branches()
#     # Сохраним список филиалов в state, чтобы позднее по ID найти нужный
#     await state.update_data(branches=branches)

#     # Формируем кнопки
#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text=f"{branch['name']} ({branch['address']})",
#                     callback_data=f"branch_id_{branch['id']}"
#                 )
#             ]
#             for branch in branches
#         ]
#     )

#     await message.answer("Выберите филиал:", reply_markup=keyboard)
#     # Устанавливаем состояние branch для обработки следующего шага
#     await state.set_state(GetService.branch)

# @router.callback_query(GetService.branch, F.data.startswith("branch_id_"))
# async def get_branch(callback: CallbackQuery, state: FSMContext):
#     """
#     Обработка выбора филиала кнопкой.
#     Сохраняем branch_id, формируем итоговое сообщение
#     с кнопками "Сохранить" / "Изменить".
#     """
#     user_data = await state.get_data()
#     branches = user_data.get("branches", [])

#     # Извлекаем ID филиала из callback_data (формат "branch_id_{id}")
#     branch_id_str = callback.data.split("branch_id_")[-1]
#     branch_id = int(branch_id_str)

#     # Ищем в сохранённом списке филиалов нужный
#     selected_branch = next((b for b in branches if b["id"] == branch_id), None)

#     # Если филиал найден, сохраняем ID и название
#     if selected_branch:
#         await state.update_data(branch_id=branch_id, branch_name=selected_branch["name"])

#     # Формируем сообщение с итогом
#     user_data = await state.get_data()
#     name = user_data['name']
#     number = user_data['number']
#     city = user_data['city']
#     branch_name = user_data.get('branch_name', 'Не выбран')

#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="Сохранить", callback_data="save_data")],
#         [InlineKeyboardButton(text="Изменить", callback_data="change")]
#     ])

#     msg = (
#         f"Ваши данные:\n\n"
#         f"ФИО: {name}\n"
#         f"Номер: {number}\n"
#         f"Город: {city}\n"
#         f"Филиал: {branch_name}\n\n"
#         f"Если все верно, нажмите 'Сохранить'."
#     )

#     await callback.message.edit_text(text=msg, reply_markup=keyboard)

# @router.callback_query(F.data == "change")
# async def change_data(callback: CallbackQuery, state: FSMContext):
#     """Если пользователь хочет изменить данные, начинаем всё заново."""
#     await state.clear()
#     await callback.message.edit_text("Введите ваше имя:")
#     await state.set_state(GetService.name)

# @router.callback_query(F.data == "save_data")
# async def save_user_data(callback: CallbackQuery, state: FSMContext):
#     """Сохраняем данные в БД/CRM и присылаем итоговое сообщение."""
#     telegram_chat_id = callback.message.chat.id

#     data = await state.get_data()
#     name = data['name']
#     number = data['number']
#     city = data['city']
#     branch_id = data.get('branch_id', 0)  # 0 или другой дефолт, если что-то пошло не так

#     # Формируем payload для запроса
#     payload = {
#         "name": name,
#         "number": number,
#         "city": city,
#         "telegram_chat_id": str(telegram_chat_id),
#         "branch_id": branch_id
#     }

#     response = await post_request_register(data=payload)
    
#     # Формируем ответ для пользователя
#     formatted_response = (
#         f"🎉 Регистрация завершена! 🎉\n\n"
#         f"👤 ФИО: {response['name']}\n"
#         f"🌍 Город: {response['city']}\n"
#         f"📞 Номер: {response['number']}\n\n"
#         f"🪪 Код: {response['code']}\n"
#     )

#     kb = [[types.KeyboardButton(text="Главное меню")]]
#     keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

#     # Редактируем текущее сообщение (с кнопками) на итоговый текст
#     await callback.message.edit_text(formatted_response)

#     address = await get_address()

#     # Дополнительная информация
#     info = (
#         f"Нажмите чтобы скопировать:\n\n"
#         f"<code>{address['name1']}{response['code']}\n\n"
#         f"{address['name2']}\n\n"
#         f"{address['name3']}{response['code']}</code>"
#     )

#     photo_filenames = [
#         "./images/taobao.jpg", 
#         "./images/pinduoduo.jpg", 
#         "./images/poizon.jpg", 
#         "./images/1688.jpg"
#     ]
#     media_group = [InputMediaPhoto(media=FSInputFile(filename)) for filename in photo_filenames]

#     # Очищаем состояние
#     await state.clear()

#     # Отправляем сообщение с инструкцией
#     await callback.message.answer(info, reply_markup=keyboard, parse_mode="HTML")

#     # Отправляем картинки группой
#     await callback.message.bot.send_media_group(
#         chat_id=callback.message.chat.id, 
#         media=media_group
#     )
