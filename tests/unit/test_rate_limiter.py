"""Tests for rate limiter."""

import time

from cs_mcp.policies.enforcement import RateLimiter


def test_rate_limiter_allows_under_limit():
    limiter = RateLimiter()
    for _ in range(5):
        assert limiter.allow("agent1", "tool1", per_minute=10)


def test_rate_limiter_blocks_over_limit():
    limiter = RateLimiter()
    for _ in range(3):
        limiter.allow("agent2", "tool2", per_minute=3)
    assert not limiter.allow("agent2", "tool2", per_minute=3)
