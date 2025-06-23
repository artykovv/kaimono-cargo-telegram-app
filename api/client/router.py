from fastapi import APIRouter, Depends

from fastapi.security.api_key import APIKey
from conf.api_conf import get_api_key
from functions.sendMessage import handle_update_success

router = APIRouter(prefix="/client")

@router.post("/update/success/{telegram_chat_id}")
async def register_success(
    telegram_chat_id: str,
    api_key: APIKey = Depends(get_api_key)
):
    await handle_update_success(chat_id=telegram_chat_id)
    return {
        "message": "success"
    }