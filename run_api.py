import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.message.router import router as message
from api.notification.router import router as notification
from api.registration.router import router as registration
from api.client.router import router as client

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы
    allow_headers=["*"],  # Разрешить все заголовки
)

app.include_router(message)
app.include_router(notification)
app.include_router(registration)
app.include_router(client)


@app.get("/")
async def base_req():
    return {"message": "hello world"}


async def run_api():
    # Запускаем Uvicorn в новом процессе
    process = await asyncio.create_subprocess_exec(
        'uvicorn', 'run_api:app', '--host', '0.0.0.0', '--port', '8000', '--reload'
    )
    await process.wait()