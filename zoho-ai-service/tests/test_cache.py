from unittest.mock import patch

import pytest

from services.cache import TTLCache


@pytest.fixture
def cache():
    return TTLCache()


class TestTTLCache:
    def test_get_set_unexpired(self, cache):
        cache.set("key1", "value1", ttl_seconds=60)
        assert cache.get("key1") == "value1"

    def test_get_expired(self, cache):
        with patch("time.time") as mock_time:
            mock_time.return_value = 1000.0
            cache.set("key_exp", "val", ttl_seconds=10)
            mock_time.return_value = 1011.0
            assert cache.get("key_exp") is None

    def test_invalidate(self, cache):
        cache.set("k", "v")
        cache.invalidate("k")
        assert cache.get("k") is None

    def test_clear(self, cache):
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None
