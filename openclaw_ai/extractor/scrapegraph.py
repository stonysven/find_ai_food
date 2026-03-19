"""Extraction logic backed by ScrapeGraph."""

from __future__ import annotations

import os
import signal

from ..config import AppConfig

EXTRACTION_PROMPT = """
Analyze the webpage content from the provided URL and determine whether it is related to AI.
Focus on topics such as LLM, RAG, agents, MCP, prompt engineering, AI applications,
model training, inference, vector databases, orchestration frameworks, and evaluation.

Return only valid JSON with this exact structure:
{
  "title": "",
  "summary": "",
  "key_points": [],
  "tech_stack": [],
  "topics": []
}

Rules:
- If the page is not AI-related, still return valid JSON but keep summary concise and topics empty.
- "key_points" should contain short bullet-style strings.
- "tech_stack" should list tools, frameworks, models, or platforms mentioned.
- "topics" should contain normalized AI tags when relevant, such as: RAG, Agent, LLM, MCP,
  Prompt Engineering, AI Application, Vector Database, Fine-tuning.
- Do not include any explanation outside JSON.
""".strip()

_HAS_WARNED_IMPORT = False
_HAS_WARNED_API_KEY = False


class ExtractionTimeoutError(Exception):
    """Raised when content extraction exceeds the configured timeout."""


def _normalize_list(value: object) -> list[str]:
    """Normalize a result field into a list of strings."""
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _timeout_handler(signum: int, frame: object) -> None:
    """Raise a timeout error when the alarm signal fires."""
    raise ExtractionTimeoutError("content extraction timed out")


def extract_content(url: str) -> dict | None:
    """Extract structured AI-related content from a URL with ScrapeGraphAI."""
    global _HAS_WARNED_IMPORT, _HAS_WARNED_API_KEY

    try:
        from scrapegraphai.graphs import SmartScraperGraph
    except ImportError:
        if not _HAS_WARNED_IMPORT:
            print("未安装 scrapegraphai，extract_content() 将跳过所有内容。")
            _HAS_WARNED_IMPORT = True
        return None

    api_key = os.getenv("SCRAPEGRAPH_API_KEY", "")
    if not api_key:
        if not _HAS_WARNED_API_KEY:
            print("未检测到 SCRAPEGRAPH_API_KEY，extract_content() 将跳过所有内容。")
            _HAS_WARNED_API_KEY = True
        return None

    model_provider = os.getenv("SCRAPEGRAPH_MODEL_PROVIDER", "openai")
    model = os.getenv("SCRAPEGRAPH_MODEL", "glm-5")
    base_url = os.getenv("SCRAPEGRAPH_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
    model_tokens = int(os.getenv("SCRAPEGRAPH_MODEL_TOKENS", "128000"))
    timeout_seconds = int(os.getenv("SCRAPEGRAPH_TIMEOUT_SECONDS", "30"))

    try:
        config: dict = {}

        if base_url:
            from scrapegraphai.models.oneapi import OneApi

            llm_model_instance = OneApi(
                model=model,
                api_key=api_key,
                base_url=base_url,
            )
            config["llm"] = {
                "model_instance": llm_model_instance,
                "model_tokens": model_tokens,
            }
        else:
            config["llm"] = {
                "api_key": api_key,
                "model_provider": model_provider,
                "model": model,
            }

        graph = SmartScraperGraph(
            prompt=EXTRACTION_PROMPT,
            source=url,
            config=config,
        )
        if hasattr(signal, "SIGALRM") and timeout_seconds > 0:
            previous_handler = signal.getsignal(signal.SIGALRM)
            signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(timeout_seconds)
            try:
                result = graph.run()
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, previous_handler)
        else:
            result = graph.run()
    except ExtractionTimeoutError:
        print(f"ScrapeGraphAI 提取超时，已跳过: {url}")
        return None
    except Exception as exc:
        print(f"ScrapeGraphAI 提取失败: {url} -> {exc}")
        return None

    if not isinstance(result, dict):
        return None

    return {
        "title": result.get("title", ""),
        "summary": result.get("summary", ""),
        "key_points": _normalize_list(result.get("key_points", [])),
        "tech_stack": _normalize_list(result.get("tech_stack", [])),
        "topics": _normalize_list(result.get("topics", [])),
    }


class ScrapeGraphExtractor:
    """Extract structured content from collected resource items."""

    def __init__(self, config: AppConfig) -> None:
        """Initialize the extractor with shared application configuration."""
        self.config = config

    def extract(self, items: list[dict]) -> list[dict]:
        """Extract normalized metadata from raw resource items."""
        os.environ["SCRAPEGRAPH_API_KEY"] = self.config.scrapegraph_api_key
        os.environ["SCRAPEGRAPH_MODEL_PROVIDER"] = self.config.scrapegraph_model_provider
        os.environ["SCRAPEGRAPH_MODEL"] = self.config.scrapegraph_model
        os.environ["SCRAPEGRAPH_BASE_URL"] = self.config.scrapegraph_base_url
        os.environ["SCRAPEGRAPH_MODEL_TOKENS"] = str(self.config.scrapegraph_model_tokens)
        os.environ["SCRAPEGRAPH_TIMEOUT_SECONDS"] = str(
            self.config.scrapegraph_timeout_seconds
        )
        extracted_items: list[dict] = []

        for item in items:
            url = item.get("url", "")
            extracted = extract_content(url)
            if not extracted:
                continue

            enriched_item = {**item, **extracted}
            extracted_items.append(enriched_item)

        return extracted_items
