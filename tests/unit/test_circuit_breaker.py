"""Tests for circuit breaker."""

from cs_agents.circuit_breaker import CircuitBreaker, CircuitState


def test_circuit_opens_after_failures():
    cb = CircuitBreaker(failure_threshold=3)
    for _ in range(3):
        cb.record_failure()
    assert cb.state == CircuitState.OPEN
    assert not cb.allow_request()


def test_circuit_recovers():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.01)
    cb.record_failure()
    cb.record_failure()
    import time
    time.sleep(0.02)
    assert cb.allow_request()
