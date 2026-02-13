import functools
import os

from fastapi import HTTPException, Request

from app.services.redis import redis_client


def rate_limiter(limit: int, window: int, prefix: str = "rate"):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if os.getenv("TESTING") == "true":
                return await func(*args, **kwargs)
            request: Request | None = kwargs.get("request")

            if request is None:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if request is None:
                raise RuntimeError("Request object not found in route")

            identifier = request.client.host
            key = f"{prefix}:{identifier}"

            current = await redis_client.incr(key)

            if current == 1:
                await redis_client.expire(key, window)

            if current > limit:
                raise HTTPException(
                    status_code=429, detail="Too many requests. Please try again later."
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
