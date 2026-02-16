import os
from unittest.mock import AsyncMock

from redis.asyncio import Redis

# Environment detection
REDIS_URL = os.getenv("REDIS_URL")
TESTING = os.getenv("TESTING", "false").lower() == "true"

# Initialize redis_client
if TESTING:
    # During tests or CI, use a mock
    redis_client: Redis | AsyncMock = AsyncMock()
elif REDIS_URL:
    # Production: connect to real Redis
    redis_client: Redis = Redis.from_url(
        REDIS_URL,
        decode_responses=True,
        socket_keepalive=True,
    )
else:
    raise RuntimeError("REDIS_URL must be set in production")
