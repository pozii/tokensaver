"""cache_store / cache_get / cache_invalidate tools."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import diskcache

_CACHE_DIR = Path.home() / ".tokensaver" / "cache"
_cache: diskcache.Cache | None = None


def _get_cache() -> diskcache.Cache:
    global _cache
    if _cache is None:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _cache = diskcache.Cache(str(_CACHE_DIR))
    return _cache


def _make_key(key: str, namespace: str) -> str:
    return f"{namespace}:{key}"


def make_cache_key(tool_name: str, args: dict) -> str:
    """Helper: deterministic cache key from tool name + sorted args."""
    raw = tool_name + json.dumps(args, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def cache_store(
    key: str,
    value: str,
    ttl_seconds: int = 3600,
    namespace: str = "default",
) -> dict:
    """
    Store a tool result in the persistent cache with a TTL.
    Prevents re-running the same expensive operation twice.
    Recommended: set key = make_cache_key(tool_name, args).

    Args:
        key: Cache key (use make_cache_key helper for deterministic keys).
        value: Result to store (JSON string or plain text).
        ttl_seconds: How long to keep (default 1 hour). Use 0 for no expiry.
        namespace: Logical group (e.g. "web", "files", "default").

    Returns:
        stored, key, expires_at (ISO timestamp)
    """
    c = _get_cache()
    full_key = _make_key(key, namespace)
    expire = ttl_seconds if ttl_seconds > 0 else None
    c.set(full_key, value, expire=expire)
    expires_at = (
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + ttl_seconds))
        if ttl_seconds > 0
        else "never"
    )
    return {"stored": True, "key": key, "expires_at": expires_at}


def cache_get(key: str, namespace: str = "default") -> dict:
    """
    Retrieve a cached result. If hit, skip re-running the original tool.

    Args:
        key: Cache key used in cache_store.
        namespace: Must match the namespace used in cache_store.

    Returns:
        hit (bool), value (str or null), key, ttl_remaining_seconds
    """
    c = _get_cache()
    full_key = _make_key(key, namespace)
    value = c.get(full_key, default=None)
    if value is None:
        return {"hit": False, "value": None, "key": key, "ttl_remaining_seconds": None}
    # diskcache doesn't expose TTL remaining directly; compute from expire time
    expire_time = c.get(full_key, expire_time=True)
    ttl_remaining = None
    if isinstance(expire_time, (int, float)):
        ttl_remaining = max(0, int(expire_time - time.time()))
    return {"hit": True, "value": value, "key": key, "ttl_remaining_seconds": ttl_remaining}


def cache_invalidate(key: str, namespace: str = "default") -> dict:
    """
    Remove a stale cache entry (e.g. after file changes).

    Args:
        key: Cache key to remove.
        namespace: Must match the namespace used in cache_store.

    Returns:
        invalidated (bool)
    """
    c = _get_cache()
    full_key = _make_key(key, namespace)
    existed = full_key in c
    c.delete(full_key)
    return {"invalidated": existed}
