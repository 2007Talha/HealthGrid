"""
Swasthya Records - Rate Limiting Core
Sliding-window in-memory rate limiter protecting expensive Gemini, OR-Tools, and simulation endpoints.
"""

import time
from collections import defaultdict
from typing import Dict, List
from fastapi import Request, HTTPException, status
from backend.app.core.config import settings

class SlidingWindowRateLimiter:
    def __init__(self, limit_per_minute: int = 60):
        self.limit = limit_per_minute
        self.window_seconds = 60
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_rate_limited(self, client_key: str) -> bool:
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean older requests
        timestamps = [ts for ts in self.requests[client_key] if ts > window_start]
        self.requests[client_key] = timestamps

        if len(timestamps) >= self.limit:
            return True

        self.requests[client_key].append(now)
        return False

limiter = SlidingWindowRateLimiter(limit_per_minute=settings.RATE_LIMIT_PER_MINUTE)

def rate_limit(request: Request):
    """
    FastAPI dependency to rate limit requests based on client IP or forwarded host.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()

    if limiter.is_rate_limited(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {limiter.limit} requests per minute. Please try again later.",
            headers={"Retry-After": "60"}
        )
