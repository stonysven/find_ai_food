"""Application entry point for the OpenClaw AI project."""

from __future__ import annotations

import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from openclaw_ai.config import AppConfig
    from openclaw_ai.extractor.scrapegraph import extract_content
    from openclaw_ai.processor.classifier import classify_content
    from openclaw_ai.processor.deduplicator import is_duplicate, mark_processed
    from openclaw_ai.processor.filter import filter_content
    from openclaw_ai.sources.bilibili import fetch_bilibili_videos
    from openclaw_ai.sources.github import fetch_github_projects
    from openclaw_ai.sources.youtube import fetch_youtube_videos
    from openclaw_ai.writer.obsidian_writer import write_to_obsidian
else:
    from .config import AppConfig
    from .extractor.scrapegraph import extract_content
    from .processor.classifier import classify_content
    from .processor.deduplicator import is_duplicate, mark_processed
    from .processor.filter import filter_content
    from .sources.bilibili import fetch_bilibili_videos
    from .sources.github import fetch_github_projects
    from .sources.youtube import fetch_youtube_videos
    from .writer.obsidian_writer import write_to_obsidian


def run() -> None:
    """Run the end-to-end collection pipeline."""
    config = AppConfig()
    if config.scrapegraph_api_key:
        os.environ["SCRAPEGRAPH_API_KEY"] = config.scrapegraph_api_key
    else:
        print("未检测到 SCRAPEGRAPH_API_KEY，提取阶段可能会跳过所有内容。")

    items = []
    print("开始获取 GitHub 数据...")
    items.extend(fetch_github_projects(config.github_topics or None))
    print("开始获取 YouTube 数据...")
    items.extend(fetch_youtube_videos(config.youtube_queries or None))
    print("开始获取 Bilibili 数据...")
    items.extend(fetch_bilibili_videos(config.bilibili_queries or None))

    print(f"采集完成，共获取 {len(items)} 条候选内容。")
    success_count = 0

    try:
        for item in items:
            if is_duplicate(item):
                print(f"跳过重复内容: {item.get('title', '')}")
                continue

            extracted = extract_content(item.get("url", ""))
            if not extracted:
                print(f"提取失败或无结果: {item.get('title', '')}")
                continue

            processed_item = {**item, **extracted}
            category = classify_content(processed_item)
            processed_item["category"] = category

            if not filter_content(processed_item):
                print(f"内容被过滤: {processed_item.get('title', '')}")
                continue

            write_to_obsidian(processed_item, category)
            mark_processed(processed_item)
            success_count += 1
            print(f"处理成功: {processed_item.get('title', '')}")
    except KeyboardInterrupt:
        print("\n已停止运行。当前已处理的内容不会丢失。")
        return

    if success_count == 0:
        print("本次没有写入任何内容。请检查依赖安装、API Key 和过滤条件。")


if __name__ == "__main__":
    run()
