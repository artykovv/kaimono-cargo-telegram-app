from aiogram import Router, F
from aiogram.types import CallbackQuery

from functions.func import get_products_status_in_china

router = Router()

@router.callback_query(F.data == "china")
async def main(callback: CallbackQuery):
    telegram_chat_id = callback.message.chat.id
    response = await get_products_status_in_china(telegram_chat_id=telegram_chat_id)

    if 'message' in response and response['message'] == "No products found for this client":
        info = "Не найдено"
        await callback.message.edit_text(info)
    else:
        # Формируем базовую информацию о пользователе

        products = response['products']

        total_amout_products = len(products)

        info = (
            f"🇨🇳🇨🇳🇨🇳\n\n"
            f"Товары на складе Китай\n\n"
            f"📦 Общее количество товаров: {total_amout_products}\n\n"
            f"Товары:\n"
            f"⬇️⬇️⬇️\n\n"
        )

        
        if products:
            # Проверяем количество товаров
            if len(products) == 1:
                # Обработка случая с одним товаром
                product = products[0]
                product_info = (
                    f"Трек номер: {product['product_code']}\n"
                    f"Статус: {product['status']}\n"
                    f"Дата: {product['date']}\n"
                )
                info += product_info
            else:
                # Обработка случая с несколькими товарами
                for product in products:
                    product_info = (
                        f"Трек номер: {product['product_code']}\n"
                        f"Статус: {product['status']}\n"
                        f"Дата: {product['date']}\n\n"
                    )
                    info += product_info
        else:
            info += "Нет товаров на складе."

        await callback.message.edit_text(info)