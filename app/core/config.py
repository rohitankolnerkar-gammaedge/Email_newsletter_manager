import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL=os.getenv("DATABASE_URL")
DATABASE_URL = "postgresql+asyncpg://postgres.ukigdqzwgmtvganudtuk:Rohit%40143242@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"
