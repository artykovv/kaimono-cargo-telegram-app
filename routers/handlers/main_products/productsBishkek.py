from aiogram import Router, F
from aiogram.types import CallbackQuery

from functions.func import get_products_status_in_bishkek, get_profile_user, get_text

router = Router()

@router.callback_query(F.data == "pickup")
async def main(callback: CallbackQuery):
    telegram_chat_id = callback.message.chat.id
    response = await get_products_status_in_bishkek(telegram_chat_id=telegram_chat_id)
    user_branch = await get_profile_user(telegram_chat_id)
    branch_address = user_branch[0]['branch']['address']
    adress = await get_text(key="adress")

    if 'message' in response and response['message'] == "No products found for this client":
        info = "Не найдено товаров для данного клиента."
        await callback.message.edit_text(info)
    else:
        # Формируем базовую информацию о пользователе
        products = response.get('products', [])

        total_count_products = len(products)
        info = (
            f"📬📬📬\n\n"
            f"Товары на складе Бишкек\n\n"
            f"Можно забрать\n\n"
            f"📦 Общее количество товаров: {total_count_products}\n"
            f"💰 Общая стоимость: {response['total_price']} сом\n"
            f"⚖️ Общий вес: {response['total_weight']} кг\n\n"
            f"Товары:\n"
            f"⬇️⬇️⬇️\n\n"
        )

        adress = (
            f"\n📍 Можете забрать: {branch_address}\n"
            f"{adress}"
        )

        if products:
            # Обработка одного товара
            if len(products) == 1:
                product = products[0]
                product_info = (
                    f"Трек номер: {product['product_code']}\n"
                    f"Вес: {product['weight']} кг\n"
                    f"Цена: {product['price']} сом\n"
                    f"Дата: {product['date']}\n"
                )
                info += product_info
            else:
                # Обработка нескольких товаров
                for product in products:
                    product_info = (
                        f"Трек номер: {product['product_code']}\n"
                        f"Вес: {product['weight']} кг\n"
                        f"Цена: {product['price']} сом\n"
                        f"Дата: {product['date']}\n\n"

                    )
                    info += product_info
        else:
            info += "Нет товаров на складе."

        await callback.message.edit_text(info)
        await callback.message.answer(adress, disable_web_page_preview=True)