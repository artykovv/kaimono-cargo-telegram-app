from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.environ.get("bot_token")
api_key = os.environ.get("api_key")
host = os.environ.get("host")

API_KEYS = {
    os.getenv("API_KEY_1"): "Key1",
    os.getenv("API_KEY_2"): "Key2",
    os.getenv("API_KEY_3"): "Key3",
}

REGISTER_SITE_URL=os.environ.get("REGISTER_SITE_URL")

ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "-1002765418724"))

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))  # Преобразуем в int
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
