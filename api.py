import asyncio
from fastapi import Depends, FastAPI
from typing import List
from pydantic import BaseModel
from fastapi.security.api_key import APIKey
from fastapi.middleware.cors import CORSMiddleware


from conf.api_conf import get_api_key
from functions.sendMessage import handle_broadcast_text, send_notification_china, send_notification_bihkek, send_notification_in_transit, send_photo_handle

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы
    allow_headers=["*"],  # Разрешить все заголовки
)

class Message(BaseModel):
    text: str
    chat_ids: list[int] = None

class Message_Photo(BaseModel):
    photos: list[str]
    message: str
    chat_ids: list[int] = None

@app.get("/")
async def base_req():
    return {"message": "hello world"}

@app.post("/api/v1/send_message")
async def send_message(
    message: Message,
    api_key: APIKey = Depends(get_api_key)
    ):
    print(message)
    await handle_broadcast_text(text=message.text, chat_ids=message.chat_ids)
    return {"message": "done"}

@app.post("/api/v1/send_photo")
async def send_message(
    q: Message_Photo
    ):
    print(q)
    await send_photo_handle(photos=q.photos, message=q.message, chat_ids=q.chat_ids)
    return {"message": "done"}


@app.post("/api/v1/notification/china")
async def send_notification_product_status_china(data: List[dict], api_key: APIKey = Depends(get_api_key)):
    asyncio.create_task(send_notification_china(data=data))
    return {"message": "done"}

@app.post("/api/v1/notification/transit")
async def send_notification_product_status_transit(data: List[dict], api_key: APIKey = Depends(get_api_key)):
    asyncio.create_task(send_notification_in_transit(data=data))
    return {"message": "done"}

@app.post("/api/v1/notification/bishkek")
async def send_notification_product_status_bishkek(data: List[dict], api_key: APIKey = Depends(get_api_key)):
    asyncio.create_task(send_notification_bihkek(data=data))
    return {"message": "done"}



async def run_api():
    # Запускаем Uvicorn в новом процессе
    process = await asyncio.create_subprocess_exec(
        'uvicorn', 'api:app', '--host', '0.0.0.0', '--port', '9090', '--reload'
    )
    await process.wait()