"""Filtering logic for collected resources."""

from __future__ import annotations

from ..config import AppConfig

AI_KEYWORDS = [
    "ai",
    "llm",
    "prompt",
    "rag",
    "agent",
    "mcp",
    "langchain",
    "language model",
    "retrieval",
]
PLACEHOLDER_TITLES = {
    "na",
    "n/a",
    "introduction",
    "video player page",
}
LOW_QUALITY_MARKERS = [
    "video player interface",
    "video player ui",
    "playback controls",
    "tap to unmute",
    "retrieving sharing information",
    "error occurred while retrieving sharing information",
    "no substantive content available",
    "no substantive information",
    "generic video player interface",
    "an error occurred",
]


def filter_content(item: dict) -> bool:
    """Return True when the item passes quality and relevance checks."""
    title = str(item.get("title", "")).strip()
    summary = str(item.get("summary", "")).strip()

    if title.lower() in PLACEHOLDER_TITLES:
        return False

    if len(summary) < 50:
        return False

    searchable_parts = [
        title,
        summary,
        " ".join(item.get("topics", [])),
        " ".join(item.get("key_points", [])),
        " ".join(item.get("tech_stack", [])),
        item.get("description", ""),
    ]
    searchable_text = " ".join(str(part).lower() for part in searchable_parts)

    if any(marker in searchable_text for marker in LOW_QUALITY_MARKERS):
        return False

    if not any(keyword in searchable_text for keyword in AI_KEYWORDS):
        return False

    if item.get("source") in {"youtube", "bilibili"}:
        topics = item.get("topics", [])
        key_points = item.get("key_points", [])
        tech_stack = item.get("tech_stack", [])
        if not topics and not key_points and not tech_stack:
            return False

    if item.get("source") == "github":
        try:
            stars = int(item.get("stars", 0))
        except (TypeError, ValueError):
            stars = 0

        if stars < 100:
            return False

    return True


class ResourceFilter:
    """Filter resources according to quality or relevance rules."""

    def __init__(self, config: AppConfig) -> None:
        """Initialize the filter with shared application configuration."""
        self.config = config

    def apply(self, items: list[dict]) -> list[dict]:
        """Filter out items that do not match project requirements."""
        return [item for item in items if filter_content(item)]
