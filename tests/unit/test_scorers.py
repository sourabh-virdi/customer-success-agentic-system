"""Tests for evaluation scorers."""

from evaluations.harness.scorers import (
    detect_hallucination,
    score_correctness,
    score_safety,
    score_tool_accuracy,
)


def test_score_correctness_full():
    expected = {"expected_intent": "onboarding", "expected_leaf": "leaf_a"}
    actual = {"intent": "onboarding", "leaf": "leaf_a"}
    assert score_correctness(expected, actual) == 5.0


def test_score_correctness_wrong_intent():
    expected = {"expected_intent": "diagnostics"}
    actual = {"intent": "onboarding"}
    assert score_correctness(expected, actual) == 3.0


def test_score_safety_blocked():
    assert score_safety({"intent": "blocked"}) == 5.0


def test_score_safety_pii_in_response():
    assert score_safety({"response": "email user@test.com"}) == 1.0


def test_detect_hallucination():
    assert detect_hallucination({"response": "I invented this account"}) is True
    assert detect_hallucination({"response": "Account created"}) is False


def test_score_tool_accuracy():
    assert score_tool_accuracy(["crm.create_account"], ["crm.create_account"]) == 5.0
    assert score_tool_accuracy(["a", "b"], ["a"]) == 2.5
