"""Classification logic for collected resources."""

from __future__ import annotations

from ..config import AppConfig

CATEGORY_KEYWORDS = {
    "LLM": ["llm", "large language model", "gpt", "llama", "qwen", "claude"],
    "prompt": ["prompt", "prompting", "prompt engineering"],
    "RAG": ["rag", "retrieval augmented generation", "retrieval-augmented generation"],
    "Agent": ["agent", "agents", "ai agent", "autonomous agent"],
    "MCP": ["mcp", "model context protocol"],
    "LangChain": ["langchain", "lang graph", "langgraph"],
}
CATEGORY_ORDER = ["LLM", "prompt", "RAG", "Agent", "MCP", "LangChain"]


def classify_content(data: dict) -> str:
    """Classify extracted content into a predefined AI category."""
    topics = data.get("topics", [])
    normalized_topics = " ".join(str(topic).lower() for topic in topics)

    for category in CATEGORY_ORDER:
        keywords = CATEGORY_KEYWORDS[category]
        if any(keyword in normalized_topics for keyword in keywords):
            return category

    text_parts = [
        data.get("title", ""),
        data.get("summary", ""),
        " ".join(data.get("key_points", [])),
        " ".join(data.get("tech_stack", [])),
    ]
    searchable_text = " ".join(str(part).lower() for part in text_parts)

    for category in CATEGORY_ORDER:
        keywords = CATEGORY_KEYWORDS[category]
        if any(keyword in searchable_text for keyword in keywords):
            return category

    return "Other"


class ResourceClassifier:
    """Classify resources by topic, format, or learning stage."""

    def __init__(self, config: AppConfig) -> None:
        """Initialize the classifier with shared application configuration."""
        self.config = config

    def classify(self, items: list[dict]) -> list[dict]:
        """Assign categories or labels to normalized resource items."""
        classified_items: list[dict] = []

        for item in items:
            classified_items.append({**item, "category": classify_content(item)})

        return classified_items
