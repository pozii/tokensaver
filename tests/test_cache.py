"""Tests for cache_store / cache_get / cache_invalidate."""
import time

from tokensaver.tools.cache import cache_get, cache_invalidate, cache_store, make_cache_key


def test_store_and_get():
    key = make_cache_key("test_tool", {"arg": "value1"})
    cache_store(key, '{"result": 42}', ttl_seconds=60, namespace="test")
    result = cache_get(key, namespace="test")
    assert result["hit"] is True
    assert result["value"] == '{"result": 42}'


def test_miss_on_unknown_key():
    result = cache_get("nonexistent_key_xyz", namespace="test")
    assert result["hit"] is False
    assert result["value"] is None


def test_invalidate():
    key = make_cache_key("test_tool", {"arg": "invalidate_me"})
    cache_store(key, "some value", ttl_seconds=60, namespace="test")
    invalidated = cache_invalidate(key, namespace="test")
    assert invalidated["invalidated"] is True
    result = cache_get(key, namespace="test")
    assert result["hit"] is False


def test_namespace_isolation():
    key = make_cache_key("test_tool", {"arg": "ns_test"})
    cache_store(key, "ns_a_value", ttl_seconds=60, namespace="ns_a")
    result_b = cache_get(key, namespace="ns_b")
    assert result_b["hit"] is False
    result_a = cache_get(key, namespace="ns_a")
    assert result_a["hit"] is True


def test_ttl_in_response():
    key = make_cache_key("test_tool", {"arg": "ttl_test"})
    cache_store(key, "ttl_value", ttl_seconds=120, namespace="test_ttl")
    result = cache_get(key, namespace="test_ttl")
    assert result["hit"] is True


def test_make_cache_key_deterministic():
    k1 = make_cache_key("my_tool", {"b": 2, "a": 1})
    k2 = make_cache_key("my_tool", {"a": 1, "b": 2})
    assert k1 == k2
