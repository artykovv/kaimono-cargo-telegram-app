import asyncio
from typing import List
from fastapi import APIRouter, Depends

from fastapi.security.api_key import APIKey
from conf.api_conf import get_api_key
from functions.sendMessage import send_notification_china, send_notification_in_transit, send_notification_bihkek

router = APIRouter(tags=["notification"])

@router.post("/api/v1/notification/china")
async def send_notification_product_status_china(data: List[dict], api_key: APIKey = Depends(get_api_key)):
    asyncio.create_task(send_notification_china(data=data))
    return {"message": "done"}

@router.post("/api/v1/notification/transit")
async def send_notification_product_status_transit(data: List[dict], api_key: APIKey = Depends(get_api_key)):
    asyncio.create_task(send_notification_in_transit(data=data))
    return {"message": "done"}

@router.post("/api/v1/notification/bishkek")
async def send_notification_product_status_bishkek(data: List[dict], api_key: APIKey = Depends(get_api_key)):
    asyncio.create_task(send_notification_bihkek(data=data))
    return {"message": "done"}
