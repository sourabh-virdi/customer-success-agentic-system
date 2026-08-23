"""Tests for MCP response cache."""

import time

from cs_mcp.routing.cache import ResponseCache


def test_cache_hit_and_miss():
    cache = ResponseCache(ttl_seconds=10)
    cache.set("kb.search", {"query": "test"}, {"status": "ok", "results": []})
    assert cache.get("kb.search", {"query": "test"}) == {"status": "ok", "results": []}
    assert cache.get("kb.search", {"query": "other"}) is None


def test_cache_expiry():
    cache = ResponseCache(ttl_seconds=0.01)
    cache.set("kb.search", {"query": "x"}, {"status": "ok"})
    time.sleep(0.02)
    assert cache.get("kb.search", {"query": "x"}) is None


def test_cache_invalidate():
    cache = ResponseCache()
    cache.set("kb.search", {"q": "a"}, {"status": "ok"})
    cache.invalidate("kb.search")
    assert cache.get("kb.search", {"q": "a"}) is None


def test_non_read_tool_not_cached():
    cache = ResponseCache()
    cache.set("crm.create_account", {"a": 1}, {"status": "ok"})
    assert cache.get("crm.create_account", {"a": 1}) is None
