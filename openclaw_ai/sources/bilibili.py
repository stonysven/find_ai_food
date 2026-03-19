"""Bilibili source integration."""

from __future__ import annotations

import re

import requests

from ..config import AppConfig

DEFAULT_BILIBILI_KEYWORDS = [
    "LLM",
    "RAG",
    "Agent",
    "MCP",
    "AI应用",
]
BILIBILI_SEARCH_API = "https://api.bilibili.com/x/web-interface/search/type"


def fetch_bilibili_videos(keywords: list[str] | None = None) -> list[dict]:
    """Fetch Bilibili videos with the public search API."""
    search_keywords = keywords or DEFAULT_BILIBILI_KEYWORDS
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.bilibili.com"}
    videos: list[dict] = []
    seen_urls: set[str] = set()

    for keyword in search_keywords:
        if len(videos) >= 5:
            break

        params = {
            "search_type": "video",
            "keyword": keyword,
            "page": 1,
        }
        try:
            response = requests.get(
                BILIBILI_SEARCH_API,
                headers=headers,
                params=params,
                timeout=15,
            )
            response.raise_for_status()
            items = response.json().get("data", {}).get("result", [])
        except requests.RequestException:
            continue
        except ValueError:
            continue

        for item in items:
            bvid = item.get("bvid", "")
            if not bvid:
                continue

            url = f"https://www.bilibili.com/video/{bvid}"
            if url in seen_urls:
                continue

            title = re.sub(r"<[^>]+>", "", item.get("title", ""))
            videos.append(
                {
                    "title": title,
                    "url": url,
                    "source": "bilibili",
                }
            )
            seen_urls.add(url)

            if len(videos) >= 5:
                break

    return videos


class BilibiliSource:
    """Collect AI learning resources from Bilibili."""

    def __init__(self, config: AppConfig) -> None:
        """Initialize the source with shared application configuration."""
        self.config = config

    def collect(self) -> list[dict]:
        """Collect raw resource items from Bilibili."""
        keywords = self.config.bilibili_queries or DEFAULT_BILIBILI_KEYWORDS
        return fetch_bilibili_videos(keywords=keywords)
