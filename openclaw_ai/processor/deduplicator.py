"""Deduplication logic for collected resources."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ..config import AppConfig

DEDUP_FILE = Path(__file__).resolve().parents[2] / "dedup.json"


def _load_dedup_data() -> dict:
    """Load deduplication records from local storage."""
    if not DEDUP_FILE.exists():
        return {"urls": [], "title_hashes": []}

    try:
        with DEDUP_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return {"urls": [], "title_hashes": []}

    return {
        "urls": data.get("urls", []),
        "title_hashes": data.get("title_hashes", []),
    }


def _save_dedup_data(data: dict) -> None:
    """Persist deduplication records to local storage."""
    DEDUP_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _title_hash(title: str) -> str:
    """Create a stable hash for a resource title."""
    normalized_title = title.strip().lower()
    return hashlib.sha256(normalized_title.encode("utf-8")).hexdigest()


def is_duplicate(item: dict) -> bool:
    """Check whether a resource has already been processed."""
    data = _load_dedup_data()
    url = item.get("url", "")
    title = item.get("title", "")
    title_hash = _title_hash(title) if title else ""

    return url in data["urls"] or title_hash in data["title_hashes"]


def mark_processed(item: dict) -> None:
    """Record a processed resource in local deduplication storage."""
    data = _load_dedup_data()
    url = item.get("url", "")
    title = item.get("title", "")
    title_hash = _title_hash(title) if title else ""

    if url and url not in data["urls"]:
        data["urls"].append(url)
    if title_hash and title_hash not in data["title_hashes"]:
        data["title_hashes"].append(title_hash)

    _save_dedup_data(data)


class ResourceDeduplicator:
    """Remove duplicated resources from the processing pipeline."""

    def __init__(self, config: AppConfig) -> None:
        """Initialize the deduplicator with shared application configuration."""
        self.config = config

    def deduplicate(self, items: list[dict]) -> list[dict]:
        """Remove duplicate items based on resource identity rules."""
        unique_items: list[dict] = []

        for item in items:
            if is_duplicate(item):
                continue

            mark_processed(item)
            unique_items.append(item)

        return unique_items
