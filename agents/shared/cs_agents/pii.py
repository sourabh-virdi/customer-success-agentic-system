"""PII detection and redaction utilities."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

DEFAULT_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "phone": r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "api_key": r"\b(?:sk|api)[-_]?[a-zA-Z0-9]{16,}\b",
}


def load_pii_patterns(path: Path | None = None) -> dict[str, str]:
    if path and path.exists():
        with path.open() as f:
            data = yaml.safe_load(f) or {}
        return data.get("patterns", DEFAULT_PATTERNS)
    return DEFAULT_PATTERNS


def redact_text(text: str, patterns: dict[str, str] | None = None) -> tuple[str, list[str]]:
    patterns = patterns or DEFAULT_PATTERNS
    matched: list[str] = []
    result = text
    for name, pattern in patterns.items():
        if re.search(pattern, result, re.IGNORECASE):
            matched.append(name)
            result = re.sub(pattern, f"[REDACTED_{name.upper()}]", result, flags=re.IGNORECASE)
    return result, matched


def redact_dict(data: Any, patterns: dict[str, str] | None = None) -> tuple[Any, list[str]]:
    patterns = patterns or DEFAULT_PATTERNS
    all_matched: list[str] = []

    if isinstance(data, str):
        return redact_text(data, patterns)
    if isinstance(data, dict):
        result = {}
        for k, v in data.items():
            redacted_v, matched = redact_dict(v, patterns)
            all_matched.extend(matched)
            result[k] = redacted_v
        return result, list(set(all_matched))
    if isinstance(data, list):
        result = []
        for item in data:
            redacted_item, matched = redact_dict(item, patterns)
            all_matched.extend(matched)
            result.append(redacted_item)
        return result, list(set(all_matched))
    return data, []
