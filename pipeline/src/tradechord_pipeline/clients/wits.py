"""WITS HTTP client: token-bucket rate limiting, on-disk cache, retries.

``get()`` returns a :class:`FetchResult` carrying an explicit
:class:`RequestStatus` instead of ``Optional[bytes]``, so callers can tell a
genuine failure apart from an empty-but-valid response.
"""

from __future__ import annotations

import hashlib
import math
import os
import threading
import time

import requests

from ..models import FetchResult, RequestStatus

RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})


def stable_key(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def ensure_dir(path: str) -> None:
    if path and not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


class TokenBucketLimiter:
    """Thread-safe global token bucket. One instance is shared across a run so the
    rate limit is genuinely global (the previous code built one per reporter-year)."""

    def __init__(self, rate_per_sec: float, burst: int | None = None):
        self.rate = max(rate_per_sec, 0.1)
        self.capacity = burst or max(1, math.ceil(self.rate))
        self.tokens = float(self.capacity)
        self.last = time.monotonic()
        self.lock = threading.Lock()

    def acquire(self) -> None:
        while True:
            with self.lock:
                now = time.monotonic()
                self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
                self.last = now
                if self.tokens >= 1:
                    self.tokens -= 1
                    return
            time.sleep(0.01)


class SimpleCache:
    """Content-addressed on-disk cache of raw responses (one file per URL).

    NOTE: kept behavior-identical to the legacy collector. Replacing this with a
    single TTL'd store is a later improvement, out of scope for this refactor.
    """

    def __init__(self, root_dir: str):
        self.root = root_dir
        ensure_dir(self.root)

    def _path(self, key: str) -> str:
        return os.path.join(self.root, f"{key}.bin")

    def get(self, key: str) -> bytes | None:
        p = self._path(key)
        if os.path.isfile(p):
            try:
                with open(p, "rb") as f:
                    return f.read()
            except OSError:
                return None
        return None

    def set(self, key: str, data: bytes) -> None:
        try:
            with open(self._path(key), "wb") as f:
                f.write(data)
        except OSError:
            pass


class WitsClient:
    def __init__(
        self,
        base_url: str,
        timeout: int,
        limiter: TokenBucketLimiter,
        cache: SimpleCache | None = None,
        retries: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.limiter = limiter
        self.cache = cache
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/xml, text/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "User-Agent": "TradeChord-Pipeline/0.1",
            }
        )

    def get(self, endpoint: str) -> FetchResult:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        key = stable_key(url)

        if self.cache:
            cached = self.cache.get(key)
            if cached is not None:
                return FetchResult(RequestStatus.SUCCESS, cached, http_status=200)

        backoff = 0.5
        last_http: int | None = None
        for _ in range(self.retries):
            self.limiter.acquire()
            try:
                resp = self.session.get(url, timeout=self.timeout)
            except requests.RequestException:
                time.sleep(backoff)
                backoff *= 2
                continue
            last_http = resp.status_code
            if resp.status_code == 200:
                if self.cache:
                    self.cache.set(key, resp.content)
                return FetchResult(RequestStatus.SUCCESS, resp.content, http_status=200)
            if resp.status_code in RETRYABLE_STATUSES:
                time.sleep(backoff)
                backoff *= 2
                continue
            return FetchResult(RequestStatus.HTTP_ERROR, None, http_status=resp.status_code)

        return FetchResult(RequestStatus.RETRY_EXHAUSTED, None, http_status=last_http)
