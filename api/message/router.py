from fastapi import APIRouter, Depends
from fastapi.security.api_key import APIKey
from conf.api_conf import get_api_key

from api.schemas import Message, Message_Photo
from functions.sendMessage import handle_broadcast_text, send_photo_handle

router = APIRouter(tags=["message"])

@router.post("/api/v1/send_message")
async def send_message(
    message: Message,
    api_key: APIKey = Depends(get_api_key)
    ):
    print(message)
    await handle_broadcast_text(text=message.text, chat_ids=message.chat_ids)
    return {"message": "done"}

@router.post("/api/v1/send_photo")
async def send_message(
    q: Message_Photo,
    api_key: APIKey = Depends(get_api_key)
    ):
    print(q)
    await send_photo_handle(photos=q.photos, message=q.message, chat_ids=q.chat_ids)
    return {"message": "done"}