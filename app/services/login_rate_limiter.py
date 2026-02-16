import functools
import os

from fastapi import HTTPException, Request

from app.services.redis import redis_client


def rate_limiter(limit: int, window: int, prefix: str = "rate"):
    """
    Rate limiter decorator for FastAPI routes.

    - limit: max requests per window
    - window: time window in seconds
    - prefix: redis key prefix
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Skip rate limiting in tests/CI
            if os.getenv("TESTING", "false").lower() == "true":
                return await func(*args, **kwargs)

            # Try to get the FastAPI request object
            request: Request | None = kwargs.get("request")
            if request is None:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            if request is None:
                raise RuntimeError("Request object not found in route")

            # Build Redis key using client IP
            identifier = request.client.host
            key = f"{prefix}:{identifier}"

            # Increment counter in Redis
            current = await redis_client.incr(key)
            if current == 1:
                await redis_client.expire(key, window)

            # Check limit
            if current > limit:
                raise HTTPException(
                    status_code=429, detail="Too many requests. Please try again later."
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
