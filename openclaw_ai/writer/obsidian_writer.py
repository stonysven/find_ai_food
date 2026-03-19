"""Obsidian writing integration."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from ..config import AppConfig

OBSIDIAN_ROOT = Path(__file__).resolve().parents[2] / "AI-Knowledge"
VALID_CATEGORIES = ["LLM", "prompt", "RAG", "Agent", "MCP", "LangChain", "Other"]


def _sanitize_filename(name: str) -> str:
    """Remove characters that are invalid in common filesystem names."""
    cleaned = re.sub(r'[\\/:*?"<>|]+', "_", name).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned[:120] or "untitled"


def _format_list_section(items: list[str]) -> str:
    """Format a list field for markdown output."""
    if not items:
        return "- None"
    return "\n".join(f"- {item}" for item in items)


def _format_tags(topics: list[str], category: str) -> str:
    """Format Obsidian tags for the note."""
    tags = []
    seen_tags: set[str] = set()

    for value in [category, *topics]:
        normalized = str(value).strip().replace(" ", "")
        if not normalized:
            continue
        tag = f"#{normalized}"
        if tag in seen_tags:
            continue
        seen_tags.add(tag)
        tags.append(tag)

    return " ".join(tags) if tags else "#Other"


def write_to_obsidian(item: dict, category: str) -> Path:
    """Write one processed item into the appropriate Obsidian note path."""
    note_category = category if category in VALID_CATEGORIES else "Other"
    target_dir = OBSIDIAN_ROOT / note_category
    target_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    title = str(item.get("title", "")).strip() or "Untitled"
    filename = f"{today}_{_sanitize_filename(title)}.md"
    note_path = target_dir / filename

    content = "\n".join(
        [
            f"# {title}",
            "",
            "## Summary",
            str(item.get("summary", "")).strip(),
            "",
            "## Key Points",
            _format_list_section(item.get("key_points", [])),
            "",
            "## Tech Stack",
            _format_list_section(item.get("tech_stack", [])),
            "",
            "## Source",
            str(item.get("url", "")).strip(),
            "",
            "## Tags",
            _format_tags(item.get("topics", []), note_category),
            "",
        ]
    )
    note_path.write_text(content, encoding="utf-8")
    return note_path


class ObsidianWriter:
    """Write processed resources into an Obsidian vault."""

    def __init__(self, config: AppConfig) -> None:
        """Initialize the writer with shared application configuration."""
        self.config = config

    def write(self, items: list[dict]) -> None:
        """Write processed items into Obsidian markdown files."""
        for item in items:
            category = item.get("category", "Other")
            write_to_obsidian(item, category)
