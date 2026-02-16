import os

from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000")
