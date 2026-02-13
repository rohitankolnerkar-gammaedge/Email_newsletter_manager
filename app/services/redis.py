import os

from dotenv import load_dotenv
from redis.asyncio import Redis

load_dotenv()

REDIS_URL = os.getenv(
    "REDIS_URL",
    "rediss://default:AZE-AAIncDI5Zjc1NTM5OGVjYjU0YjJkYTMzZWYzZmU3YmQxYmZjNXAyMzcxODI@cunning-ghoul-37182.upstash.io:6379",
)
if not REDIS_URL:
    raise RuntimeError("REDIS_URL not found in environment")

redis_client = Redis.from_url(
    REDIS_URL,
    decode_responses=True,
)
