import threading
import time
from typing import Any


class TTLCache:
    def __init__(self):
        self._store: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        with self._lock:
            self._store[key] = (time.time() + ttl_seconds, value)

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if time.time() > expires_at:
                del self._store[key]
                return None
            return value

    def invalidate(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
