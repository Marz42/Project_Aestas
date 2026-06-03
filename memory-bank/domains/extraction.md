# 提炼域（Extraction）

> WARM — DeepSeek 单条提炼与 Prompt 模板。改 AI 输出前阅读。

---

## 职责

- 将 `status=pending` 的文章调用 DeepSeek 生成结构化 insight
- 写入 `article_insights`，文章标为 `extracted`（或 `failed` / `skipped`）
- 支持 tag 绑定自定义 `prompt_templates`

## 关键代码

| 文件 | 作用 |
|------|------|
| `backend/app/services/extraction/service.py` | `ExtractionService.extract_pending` |
| `backend/app/services/extraction/llm_client.py` | OpenAI 兼容客户端（DeepSeek） |
| `backend/app/services/extraction/schemas.py` | `ArticleInsightStructured` |
| `backend/app/services/extraction/prompts.py` | 组装 system/user 消息 |
| `backend/app/services/extraction/markdown.py` | `short_news_md` 渲染 |
| `backend/app/services/extraction/seed_prompts.py` | 种子模板 |

## 状态机

```
pending → extracted   # 成功写入 insight
pending → failed      # LLM/校验失败
pending → skipped     # 正文过短等
```

重新提炼：`POST /articles/{id}/reextract`

## Prompt 解析顺序

1. 文章所属 `tag.prompt_template_id` 若存在，用该模板
2. 否则用默认 extraction 模板（种子数据）

模板字段：`system_prompt`、`user_prompt_template`（占位符替换标题、摘要等）。

## 环境与限制

- 必填：`DEEPSEEK_API_KEY`（无则提炼失败/跳过）
- 单次批量：`extract_pending(limit=20)`（Beat 兜底）；`fetch_all_feeds` 内为 limit=30
- 正文来源：`content_md` 或 `summary_raw`，截断上限见 `prompts.py`

## 结构化输出契约

见 `data-contracts.md` — `article_insights.structured` JSON 字段。

## 测试

`test_extraction_service.py`、`test_llm_client.py`、`test_extraction_markdown.py`、`test_prompts.py`、`test_prompt_templates_api.py`
