"""Tests for prompt loader."""

from cs_agents.prompts import PromptLoader


def test_render_supervisor_prompt():
    loader = PromptLoader()
    text = loader.render(
        "supervisor_system.j2",
        user_input="help",
        session_memory={},
        user_profile={},
    )
    assert "Supervisor" in text
    assert "help" in text


def test_get_version():
    loader = PromptLoader()
    version = loader.get_version("supervisor_system.j2")
    assert version == "1.0.0"
