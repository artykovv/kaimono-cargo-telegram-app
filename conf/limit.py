from aiogram import BaseMiddleware
from aiogram.types import Message
import time

class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, limit: int):
        super().__init__()
        self.limit = limit
        self.last_message = {}

    async def __call__(self, handler, event: Message, data):
        user_id = event.from_user.id
        current_time = time.time()

        if user_id in self.last_message:
            time_since_last_message = current_time - self.last_message[user_id]

            if time_since_last_message < self.limit:
                await event.answer(f"Не спамьте! Подождите {self.limit - time_since_last_message:.1f} сек.")
                return  # Прекращаем обработку сообщения

        self.last_message[user_id] = current_time
        return await handler(event, data)