"""Tests for PII redaction."""

from cs_agents.pii import redact_dict, redact_text


def test_redact_email():
    text = "Contact me at user@example.com please"
    redacted, matched = redact_text(text)
    assert "user@example.com" not in redacted
    assert "email" in matched


def test_redact_ssn():
    text = "My SSN is 123-45-6789"
    redacted, matched = redact_text(text)
    assert "123-45-6789" not in redacted
    assert "ssn" in matched


def test_redact_dict_nested():
    data = {"user": {"email": "test@example.com", "name": "John"}}
    redacted, matched = redact_dict(data)
    assert "test@example.com" not in str(redacted)
    assert "email" in matched
