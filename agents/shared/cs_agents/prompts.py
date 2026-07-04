"""Versioned Jinja2 prompt template loader."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

DEFAULT_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class PromptLoader:
    def __init__(self, prompts_dir: Path | None = None) -> None:
        self.prompts_dir = prompts_dir or DEFAULT_PROMPTS_DIR
        self.env = Environment(
            loader=FileSystemLoader(str(self.prompts_dir)),
            autoescape=select_autoescape(default_for_string=False),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, template_name: str, **kwargs: object) -> str:
        template = self.env.get_template(template_name)
        return template.render(**kwargs)

    def get_version(self, template_name: str) -> str:
        template = self.env.get_template(template_name)
        return getattr(template.module, "VERSION", "1.0.0")
