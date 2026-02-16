import os
from functools import wraps

from fastapi import HTTPException, Request

from app.services.redis import redis_client


def user_rate_limit(limit: int, window: int, prefix: str = "user"):
    """
    User-based rate limiter decorator.

    - limit: max requests per window
    - window: time window in seconds
    - prefix: redis key prefix
    """

    def decorator(func):
        @wraps(func)
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

            # Get the current user object
            current_user = kwargs.get("current_user")
            if current_user is None:
                raise RuntimeError("current_user required for user-based rate limiting")

            # Build Redis key using user ID
            identifier = current_user.id
            key = f"{prefix}:{identifier}"

            # Increment counter in Redis
            current = await redis_client.incr(key)
            if current == 1:
                await redis_client.expire(key, window)

            # Check if user exceeded limit
            if current > limit:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

            return await func(*args, **kwargs)

        return wrapper

    return decorator
