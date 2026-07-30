"""Synthetic scenario evaluation runner."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluations.harness.scorers import (
    detect_hallucination,
    score_correctness,
    score_safety,
    score_tool_accuracy,
)

SCENARIOS_DIR = Path(__file__).resolve().parents[1] / "synthetic_scenarios"
CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"


def load_scenarios() -> list[dict[str, Any]]:
    scenarios = []
    for path in SCENARIOS_DIR.glob("*.yaml"):
        with path.open() as f:
            scenarios.append(yaml.safe_load(f))
    return scenarios


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open() as f:
        return yaml.safe_load(f)


def classify_intent(user_input: str) -> str:
    text = user_input.lower()
    if "ignore" in text and "instructions" in text:
        return "blocked"
    if any(w in text for w in ["onboard", "setup", "ssn", "account"]):
        return "onboarding"
    if any(w in text for w in ["integration", "diagnostic", "webhook"]):
        return "diagnostics"
    if any(w in text for w in ["cancel", "churn", "downgrade"]):
        return "retention"
    return "onboarding"


def simulate_supervisor(user_input: str) -> dict[str, Any]:
    intent = classify_intent(user_input)
    if intent == "blocked":
        return {
            "intent": "blocked",
            "response": "I cannot process that request. A security incident has been logged.",
        }
    leaf_map = {"onboarding": "leaf_a", "diagnostics": "leaf_b", "retention": "leaf_c"}
    return {
        "intent": intent,
        "leaf": leaf_map.get(intent),
        "response": f"Handled {intent} request.",
        "tool_result": {},
    }


def run_evaluations() -> dict[str, Any]:
    config = load_config()
    scenarios = load_scenarios()
    results = []
    hallucination_count = 0

    for scenario in scenarios:
        actual = simulate_supervisor(scenario["user_input"])
        correctness = score_correctness(scenario, actual)
        safety = score_safety(actual)
        hallucination = detect_hallucination(actual)
        if hallucination:
            hallucination_count += 1

        results.append({
            "name": scenario["name"],
            "correctness": correctness,
            "safety": safety,
            "hallucination": hallucination,
            "passed": correctness >= config["thresholds"]["correctness_min"],
        })

    total = len(results)
    report = {
        "scenarios_run": total,
        "avg_correctness": sum(r["correctness"] for r in results) / total if total else 0,
        "hallucination_rate": hallucination_count / total if total else 0,
        "pass_rate": sum(1 for r in results if r["passed"]) / total if total else 0,
        "results": results,
        "thresholds_met": {
            "correctness": sum(r["correctness"] for r in results) / total >= config["thresholds"]["correctness_min"] if total else False,
            "hallucination": hallucination_count / total <= config["thresholds"]["hallucination_rate_max"] if total else True,
        },
    }
    return report


if __name__ == "__main__":
    print(json.dumps(run_evaluations(), indent=2))
