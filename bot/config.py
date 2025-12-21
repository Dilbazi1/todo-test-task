
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "твой_токен_бота")
API_URL = os.getenv("API_URL", "http://backend:8000/api/")
API_USER = os.getenv("API_USER", "admin")
API_PASS = os.getenv("API_PASS", "admin")