"""Tests for audit logger."""

from cs_mcp.policies.enforcement import AuditLogger, PIIFilter, audit_logger


def test_audit_logger_append_only():
    logger = AuditLogger()
    entry = logger.log("agent1", "s1", "tool.test", "success", "trace-1")
    assert entry.agent_id == "agent1"
    assert len(logger.get_entries()) == 1
    lines = logger.to_json_lines()
    assert "agent1" in lines


def test_pii_filter_redacts():
    filt = PIIFilter()
    redacted, matched = filt.apply({"email": "user@example.com"})
    assert "user@example.com" not in str(redacted)
    assert "email" in matched


def test_global_audit_logger():
    before = len(audit_logger.get_entries())
    audit_logger.log("a", "s", "t", "ok")
    assert len(audit_logger.get_entries()) == before + 1
