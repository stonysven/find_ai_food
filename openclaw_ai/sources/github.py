"""GitHub source integration."""

from __future__ import annotations

import requests

from ..config import AppConfig

GITHUB_SEARCH_API = "https://api.github.com/search/repositories"
DEFAULT_GITHUB_QUERIES = [
    "topic:rag stars:>300",
    "topic:llm-agent stars:>200",
    "mcp ai agent",
]


def fetch_github_projects(queries: list[str] | None = None) -> list[dict]:
    """Fetch AI-related GitHub projects and return normalized resource items."""
    search_queries = queries or DEFAULT_GITHUB_QUERIES
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "openclaw-ai",
    }
    projects: list[dict] = []
    seen_urls: set[str] = set()

    for query in search_queries:
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": 5,
        }
        try:
            response = requests.get(
                GITHUB_SEARCH_API,
                headers=headers,
                params=params,
                timeout=15,
            )
            response.raise_for_status()
            items = response.json().get("items", [])
        except requests.RequestException:
            continue
        except ValueError:
            continue

        for item in items[:5]:
            url = item.get("html_url", "")
            if not url or url in seen_urls:
                continue

            projects.append(
                {
                    "title": item.get("full_name", ""),
                    "description": item.get("description") or "",
                    "url": url,
                    "stars": item.get("stargazers_count", 0),
                    "source": "github",
                }
            )
            seen_urls.add(url)

    return projects


class GitHubSource:
    """Collect AI learning resources from GitHub."""

    def __init__(self, config: AppConfig) -> None:
        """Initialize the source with shared application configuration."""
        self.config = config

    def collect(self) -> list[dict]:
        """Collect raw resource items from GitHub."""
        queries = self.config.github_topics or DEFAULT_GITHUB_QUERIES
        return fetch_github_projects(queries=queries)
