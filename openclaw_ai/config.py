"""Configuration objects for the OpenClaw AI project."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _load_env_file() -> None:
    """Load key-value pairs from a local .env file if present."""
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def _split_csv_env(name: str, default: list[str] | None = None) -> list[str]:
    """Convert a comma-separated environment variable into a list."""
    value = os.getenv(name, "")
    if not value:
        return list(default or [])
    return [part.strip() for part in value.split(",") if part.strip()]


_load_env_file()


@dataclass
class AppConfig:
    """Store application-level configuration for data collection and writing."""

    obsidian_vault_path: str = field(
        default_factory=lambda: os.getenv("OBSIDIAN_VAULT_PATH", "")
    )
    daily_note_folder: str = field(default_factory=lambda: os.getenv("DAILY_NOTE_FOLDER", "AI"))
    github_topics: list[str] = field(
        default_factory=lambda: _split_csv_env("GITHUB_QUERIES")
    )
    youtube_queries: list[str] = field(
        default_factory=lambda: _split_csv_env("YOUTUBE_QUERIES")
    )
    bilibili_queries: list[str] = field(
        default_factory=lambda: _split_csv_env("BILIBILI_QUERIES")
    )
    scrapegraph_api_key: str = field(
        default_factory=lambda: os.getenv("SCRAPEGRAPH_API_KEY", "")
    )
    scrapegraph_model_provider: str = field(
        default_factory=lambda: os.getenv("SCRAPEGRAPH_MODEL_PROVIDER", "openai")
    )
    scrapegraph_model: str = field(
        default_factory=lambda: os.getenv("SCRAPEGRAPH_MODEL", "glm-5")
    )
    scrapegraph_base_url: str = field(
        default_factory=lambda: os.getenv(
            "SCRAPEGRAPH_BASE_URL",
            "https://open.bigmodel.cn/api/paas/v4",
        )
    )
    scrapegraph_model_tokens: int = field(
        default_factory=lambda: int(os.getenv("SCRAPEGRAPH_MODEL_TOKENS", "128000"))
    )
    scrapegraph_timeout_seconds: int = field(
        default_factory=lambda: int(os.getenv("SCRAPEGRAPH_TIMEOUT_SECONDS", "30"))
    )
