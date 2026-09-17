import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import HTTPException, Request, status

from config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS

_lock = Lock()
_request_log: dict[str, deque[float]] = defaultdict(deque)


def _client_key(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def check_rate_limit(request: Request) -> None:
    client = _client_key(request)
    now = time.monotonic()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS

    with _lock:
        log = _request_log[client]
        while log and log[0] < window_start:
            log.popleft()

        if len(log) >= RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again later.",
            )

        log.append(now)
