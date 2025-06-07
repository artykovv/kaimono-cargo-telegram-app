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