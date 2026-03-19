# OpenClaw AI

自动收集 AI 学习资料，并将整理后的内容写入 Obsidian Markdown。

## 功能简介

- 从 GitHub、YouTube、Bilibili 获取 AI 相关内容
- 使用 ScrapeGraphAI 提取结构化摘要
- 自动分类到 `LLM`、`RAG`、`Agent`、`MCP` 等目录
- 过滤低质量内容
- 通过 `dedup.json` 避免重复写入
- 输出为 Obsidian 可直接使用的 Markdown 笔记

## 项目结构

```text
openclaw_ai/
├── main.py
├── config.py
├── sources/
│   ├── github.py
│   ├── youtube.py
│   └── bilibili.py
├── extractor/
│   └── scrapegraph.py
├── processor/
│   ├── classifier.py
│   ├── deduplicator.py
│   └── filter.py
└── writer/
    └── obsidian_writer.py
```

## 安装

建议使用 Python 3.10+。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 配置

复制环境变量模板：

```bash
cp .env.example .env
```

然后编辑 `.env`，至少配置：

```env
SCRAPEGRAPH_API_KEY=your_api_key_here
```

可选配置：

```env
OBSIDIAN_VAULT_PATH=
GITHUB_QUERIES=topic:rag stars:>300,topic:llm-agent stars:>200,mcp ai agent
YOUTUBE_QUERIES=LLM,RAG,Agent,MCP,AI应用
BILIBILI_QUERIES=LLM,RAG,Agent,MCP,AI应用
```

## 运行

推荐使用模块方式运行：

```bash
python3 -m openclaw_ai.main
```

运行后会执行以下流程：

1. 拉取 GitHub、YouTube、Bilibili 内容
2. 合并为统一列表
3. 检查是否重复
4. 使用 ScrapeGraphAI 提取结构化内容
5. 自动分类
6. 过滤低质量内容
7. 写入 Obsidian
8. 记录到 `dedup.json`

## 输出目录

程序会在项目根目录下自动创建：

```text
AI-Knowledge/
├── LLM/
├── prompt/
├── RAG/
├── Agent/
├── MCP/
├── LangChain/
└── Other/
```

每篇笔记文件名格式：

```text
YYYY-MM-DD_标题.md
```

笔记内容格式：

```md
# 标题

## Summary

## Key Points

## Tech Stack

## Source
URL

## Tags
#RAG #Agent
```

## 去重规则

- 基于 `url`
- 基于 `title hash`

去重记录保存在项目根目录：

```text
dedup.json
```

## 注意事项

- 首次运行前需要先安装依赖，否则会缺少 `requests` 或 `scrapegraphai`
- `ScrapeGraphAI` 提取失败时，当前条目会被跳过
- GitHub 条目会根据 `stars` 做基础质量过滤
