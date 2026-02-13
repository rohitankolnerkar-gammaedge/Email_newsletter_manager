import os
from functools import wraps

from fastapi import HTTPException, Request

from app.services.redis import redis_client


def user_rate_limit(limit: int, window: int, prefix: str = "user"):
    def decorator(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):
            if os.getenv("TESTING") == "true":
                return await func(*args, **kwargs)

            request: Request | None = kwargs.get("request")
            current_user = kwargs.get("current_user")
            if request is None:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg

            if current_user is None:
                raise RuntimeError("current_user required for user-based rate limiting")

            identifier = current_user.id
            key = f"{prefix}:{identifier}"

            current = await redis_client.incr(key)

            if current == 1:
                await redis_client.expire(key, window)

            if current > limit:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

            return await func(*args, **kwargs)

        return wrapper

    return decorator
