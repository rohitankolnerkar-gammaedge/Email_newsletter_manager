import functools

from fastapi import HTTPException, Request

from app.services.redis import redis_client


def rate_limiter(limit: int, window: int, prefix: str = "rate"):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_user: Request | None = kwargs.get("current_user")
            if current_user is None:
                for ar in args:
                    if isinstance(ar, Request):
                        current_user = ar
                        break
            if current_user is None:
                raise RuntimeError("Request object not found in route")
            identifier = current_user.client.host
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
