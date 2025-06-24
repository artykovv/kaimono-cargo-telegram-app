from fastapi import APIRouter, Depends

from fastapi.security.api_key import APIKey
from conf.api_conf import get_api_key
from functions.sendMessage import handle_register_success

router = APIRouter()

@router.post("/registration/success/{telegram_chat_id}")
async def register_success(
    telegram_chat_id: str,
    api_key: APIKey = Depends(get_api_key)
):
    await handle_register_success(chat_id=telegram_chat_id)
    return {
        "message": "success"
    }