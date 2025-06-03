from aiogram import Router, types, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from functions.func import get_product_on_product_code

router = Router()

class SearchProductState(StatesGroup):
    waiting_for_product_code = State()

@router.message(F.text == "🔎 Поиск")
async def start_search(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Поиск товара по трек коду", callback_data="search_product_code")]
    ])
    await message.answer("Поиск по:", reply_markup=kb)

# Обработка нажатия на кнопку для поиска по трек-коду
@router.callback_query(F.data == "search_product_code")
async def search_product(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите трек код товара:")
    await state.set_state(SearchProductState.waiting_for_product_code)


@router.message(SearchProductState.waiting_for_product_code)
async def process_product_code(message: Message, state: FSMContext, bot: Bot):
    product_code = message.text

    try:
        # Предполагается, что `get_product_on_product_code` - это функция для получения информации о товаре по трек-коду
        response = await get_product_on_product_code(product_code=product_code)

        # Проверяем, что ответ не пустой
        if not response or 'status' not in response:
            await message.answer("Товар с данным трек-кодом не найден.")
        else:
            data = response

            # Обработка статусов
            if data['status'] == "В китае":
                info_china = (
                    f"🇨🇳 🇨🇳 🇨🇳\n\n"
                    f"Товар на складе Китай\n\n"
                    f"Трек номер: {data['product_code']}\n"
                    f"Статус: {data['status']}\n"
                    f"Дата: {data['date']}\n"
                )
                await message.answer(info_china)

            elif data['status'] == "В пути":
                info_transit = (
                    f"🚚 🚚 🚚\n\n"
                    f"Товар в пути\n\n"
                    f"Трек номер: {data['product_code']}\n"
                    f"Статус: {data['status']}\n"
                    f"Дата: {data['date']}\n"
                )
                await message.answer(info_transit)

            elif data['status'] == "Можно забрать":
                info_bishkek = (
                    f"📬 📬 📬\n\n"
                    f"Товар на складе Бишкек\n\n"
                    f"Трек номер: {data['product_code']}\n"
                    f"Статус: {data['status']}\n"
                    f"Дата: {data['date']}\n"
                    f"Вес: {data['weight']} кг\n"
                    f"Цена: {data['price']} сом\n"
                )
                await message.answer(info_bishkek)

            else:
                await message.answer("Статус товара не определен.")

    except Exception as e:
        await message.answer(f"Произошла ошибка при обработке трек-кода: {str(e)}")
    finally:
        await state.clear()  # Завершаем состояние после обработки

