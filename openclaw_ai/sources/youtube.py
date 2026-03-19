"""YouTube source integration."""

from __future__ import annotations

import html
import re
from urllib.parse import quote_plus

import requests

from ..config import AppConfig

DEFAULT_YOUTUBE_KEYWORDS = [
    "LLM",
    "RAG",
    "Agent",
    "MCP",
    "AI应用",
]
YOUTUBE_SEARCH_URL = "https://www.youtube.com/results"


def fetch_youtube_videos(keywords: list[str] | None = None) -> list[dict]:
    """Fetch YouTube videos with a lightweight search-page parser."""
    search_keywords = keywords or DEFAULT_YOUTUBE_KEYWORDS
    headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"}
    videos: list[dict] = []
    seen_urls: set[str] = set()

    for keyword in search_keywords:
        if len(videos) >= 5:
            break

        try:
            response = requests.get(
                f"{YOUTUBE_SEARCH_URL}?search_query={quote_plus(keyword)}",
                headers=headers,
                timeout=15,
            )
            response.raise_for_status()
        except requests.RequestException:
            continue

        matches = re.findall(
            r'"videoId":"([^"]+)".*?"title":\{"runs":\[\{"text":"([^"]+)"\}\]',
            response.text,
        )
        for video_id, title in matches:
            url = f"https://www.youtube.com/watch?v={video_id}"
            if url in seen_urls:
                continue

            videos.append(
                {
                    "title": html.unescape(title),
                    "url": url,
                    "source": "youtube",
                }
            )
            seen_urls.add(url)

            if len(videos) >= 5:
                break

    return videos


class YouTubeSource:
    """Collect AI learning resources from YouTube."""

    def __init__(self, config: AppConfig) -> None:
        """Initialize the source with shared application configuration."""
        self.config = config

    def collect(self) -> list[dict]:
        """Collect raw resource items from YouTube."""
        keywords = self.config.youtube_queries or DEFAULT_YOUTUBE_KEYWORDS
        return fetch_youtube_videos(keywords=keywords)
