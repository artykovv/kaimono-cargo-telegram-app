
from pydantic import BaseModel


class Message(BaseModel):
    text: str
    chat_ids: list[int] = None

class Message_Photo(BaseModel):
    photos: list[str]
    message: str
    chat_ids: list[int] = None