from datetime import datetime, timedelta
from typing import Dict, Optional, Callable
from functools import wraps
import asyncio

class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, list] = {}

    def __call__(self, func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            ip = kwargs.get('ip_address')
            if not ip:
                return await func(*args, **kwargs)

            now = datetime.utcnow()
            if ip not in self.requests:
                self.requests[ip] = []

            # Remove expired requests
            self.requests[ip] = [
                req for req in self.requests[ip]
                if req > now - timedelta(seconds=self.time_window)
            ]

            if len(self.requests[ip]) >= self.max_requests:
                raise Exception(f"Rate limit exceeded: {self.max_requests} requests per {self.time_window} seconds")

            self.requests[ip].append(now)
            return await func(*args, **kwargs)

        return wrapper

# Create a rate limiter instance that can be used as a decorator
def rate_limiter(max_requests: int, time_window: int):
    def decorator(func: Callable):
        limiter = RateLimiter(max_requests, time_window)
        return limiter(func)
    return decorator
