import json
import httpx
import asyncio

from conf.for_api import headers
from conf.config import host

async def validate_user_telegram_chat_id(telegram_chat_id: str) -> bool: 
    async with httpx.AsyncClient() as client:
        url = f"{host}/telegram/bool/{telegram_chat_id}"

        response = await client.get(url=url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, bool):
                return result
        else:
            return False

async def get_profile_user(telegram_chat_id: str) -> bool:
    async with httpx.AsyncClient() as client:
        url = f"{host}/telegram/{telegram_chat_id}"
        response = await client.get(url=url, headers=headers)
        return response.json()

async def post_request_register(data: dict):
    async with httpx.AsyncClient() as client:
        url = f"{host}/telegram/register/clients"
        response = await client.post(url=url, headers=headers, json=data)
        return response.json()
    
async def get_all_users_telegram_chat_ids():
    async with httpx.AsyncClient() as client:
        url = f"{host}/telegram/get/clients/telegram_chat_ids"
        response = await client.get(url=url, headers=headers)
        users = response.json()
        return users
    
async def get_products_status_in_bishkek(telegram_chat_id):
    async with httpx.AsyncClient() as client:
        url = f"{host}/telegram/products/status/inwarehouse/{telegram_chat_id}"
        response = await client.get(url=url, headers=headers)
        return response.json()

async def get_products_status_in_china(telegram_chat_id):
    async with httpx.AsyncClient() as client:
        url = f"{host}/telegram/products/status/inchina/{telegram_chat_id}"
        response = await client.get(url=url, headers=headers)
        return response.json()
    
async def get_products_status_in_transit(telegram_chat_id):
    async with httpx.AsyncClient() as client:
        url = f"{host}/telegram/products/status/intransit/{telegram_chat_id}"
        response = await client.get(url=url, headers=headers)
        return response.json()
    
async def get_product_on_product_code(product_code):
    async with httpx.AsyncClient() as client:
        url = f"{host}/telegram/product/{product_code}"
        response = await client.get(url=url, headers=headers)
        return response.json()
    
async def get_branches():
    async with httpx.AsyncClient() as client:
        url = f"{host}/branch/"
        response = await client.get(url=url, headers=headers)
        return response.json()
    
async def get_address(telegram_chat_id):
    async with httpx.AsyncClient() as client:
        url = f"{host}/address/"
        response = await client.get(url=url, headers=headers)
        user_data = await get_profile_user(telegram_chat_id=telegram_chat_id)
        user = user_data[0]
        address = response.json()
        info = (
            f"Нажмите чтобы скопировать:\n\n"
            f"<code>{address['name1']}{user['numeric_code']}\n"
            f"{address['name2']}\n"
            f"{address['name3']}{user['numeric_code']}</code>"
        )
        return info
    
async def update_branch(telegram_chat_id, branch_id):
    async with httpx.AsyncClient() as client:
        try:
            url = f"{host}/telegram/update/branch?telegram_chat_id={telegram_chat_id}&branch_id={branch_id}"
            response = await client.post(url=url, headers=headers)
            response.raise_for_status()  # Проверка на ошибки HTTP
            return response
        except httpx.HTTPStatusError as e:
            return e.response  # Возвращаем ответ с ошибкой для дальнейшей обработки
        except Exception as e:
            return httpx.Response(status_code=500, text=str(e))
        
async def get_text(key: str):
    async with httpx.AsyncClient() as client:
        try:
            url = f"{host}/textes/{key}"
            response = await client.get(url=url, headers=headers)
            response.raise_for_status()  # Проверка на ошибки HTTP
            text = response.json()
            return text["text"]
        except httpx.HTTPStatusError as e:
            return e.response  # Возвращаем ответ с ошибкой для дальнейшей обработки
        except Exception as e:
            return httpx.Response(status_code=500, text=str(e))