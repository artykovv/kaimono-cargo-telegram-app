import asyncio
import uvicorn
from bot import dp, bot
from api import run_api


async def on_startup():
    await dp.start_polling(bot)



async def main():
    # Запускаем бота и API
    await asyncio.gather(
        on_startup(),
        run_api()  # Запускаем uvicorn в отдельном процессе
    )

if __name__ == "__main__":
    asyncio.run(main())