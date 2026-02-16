# app/services/redis.py
import os
import ssl

from redis.asyncio import Redis

REDIS_URL = os.getenv("REDIS_URL")

redis_client: Redis | None = None

if REDIS_URL:
    if REDIS_URL.startswith("rediss://"):
        # Use Upstash TLS
        ssl_context = ssl.create_default_context()
        redis_client = Redis.from_url(
            REDIS_URL, decode_responses=True, ssl=ssl_context  # TLS works in redis 7+
        )
    else:
        redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
else:
    print("REDIS_URL not set")
