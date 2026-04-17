import time
import asyncio
from functools import wraps
from typing import Callable, Any, Dict, Tuple
from fastapi import HTTPException, Request
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

class RateLimiter:
    """
    An advanced sliding window rate limiter.
    """
    def __init__(self, times: int, seconds: int):
        self.times = times
        self.seconds = seconds
        self.user_history: Dict[str, list] = {}

    def is_allowed(self, user_id: str) -> Tuple[bool, int]:
        now = time.time()
        if user_id not in self.user_history:
            self.user_history[user_id] = [now]
            return True, 0

        # Filter out timestamps outside the current window
        self.user_history[user_id] = [
            t for t in self.user_history[user_id] if now - t < self.seconds
        ]

        if len(self.user_history[user_id]) < self.times:
            self.user_history[user_id].append(now)
            return True, 0

        retry_after = int(self.seconds - (now - self.user_history[user_id][0]))
        return False, retry_after

def rate_limit(times: int, seconds: int):
    """
    FastAPI compatible rate limiting decorator.
    
    Usage:
    @app.get("/")
    @rate_limit(times=5, seconds=60)
    async def root(request: Request):
        ...
    """
    limiter = RateLimiter(times, seconds)

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request object from kwargs
            request: Request = kwargs.get("request")
            if not request:
                # Attempt to find Request object in args if not in kwargs
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if not request:
                raise ValueError("Rate limiting decorator requires a 'request: Request' argument in the endpoint.")

            user_id = request.client.host  # Use IP address as user identifier
            allowed, retry_after = limiter.is_allowed(user_id)
            
            if not allowed:
                raise HTTPException(
                    status_code=HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                    headers={"Retry-After": str(retry_after)}
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
