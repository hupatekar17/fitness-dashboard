"""Tiny TTL cache decorator. Single-process, in-memory."""
from __future__ import annotations

import functools
import time
from typing import Any, Callable

_store: dict[tuple, tuple[float, Any]] = {}


def ttl_cache(seconds: int = 300) -> Callable:
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            key = (fn.__name__, args, tuple(sorted(kwargs.items())))
            now = time.time()
            if key in _store:
                ts, val = _store[key]
                if now - ts < seconds:
                    return val
            val = fn(*args, **kwargs)
            _store[key] = (now, val)
            return val
        return wrapper
    return decorator
