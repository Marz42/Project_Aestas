# 提炼域（Extraction）

> WARM — DeepSeek 单条提炼与 Prompt 模板。改 AI 输出前阅读。

---

## 职责

- 将 `status=pending` 的文章调用 DeepSeek 生成结构化 insight
- 写入 `article_insights`，文章标为 `extracted`（或 `failed` / `skipped`）
- 支持 tag 绑定自定义 `prompt_templates`

## M5a 目标：全中文 + 前台可编辑

| 要求 | 说明 |
|------|------|
| 输出语言 | `headline`、`summary`、`key_facts`、`why_it_matters` 均为**简体中文** |
| Prompt 来源 | 运行时以 `prompt_templates`（DB）为准；种子/代码默认仅用于 `seed-prompts` |
| 用户可见 | 管理后台 Prompt 页列出**全部** purpose 的模板，可新建/编辑/删除；板块可绑定 `extraction` 模板 |
| 禁止 | 聚类/简报等 Prompt 仅写死在代码中且后台不可见 |

## 关键代码

| 文件 | 作用 |
|------|------|
| `backend/app/services/extraction/service.py` | `ExtractionService.extract_pending` |
| `backend/app/services/extraction/llm_client.py` | DeepSeek + V4 `thinking: disabled` |
| `backend/app/services/extraction/schemas.py` | `ArticleInsightStructured` |
| `backend/app/services/extraction/prompts.py` | 默认模板（与种子同步） |
| `backend/app/services/extraction/seed_prompts.py` | 种子模板 |
| `frontend/src/views/PromptsView.vue` | 用户编辑入口 |

## 状态机

```
pending → extracted | failed | skipped
```

重新提炼：`POST /articles/{id}/reextract`

## Prompt 解析顺序

1. `tag.prompt_template_id` → 对应 `purpose=extraction` 模板
2. 否则 DB 中默认 extraction 模板或代码回退

## 环境与限制

- 必填：`DEEPSEEK_API_KEY`
- 批量：`extract_pending(limit=20)`；`fetch_all_feeds` 内 limit=30
- 正文：`content_md` 或 `summary_raw`，截断见 `prompts.py`

## 测试

`test_extraction_service.py`、`test_llm_client.py`、`test_prompts.py`、`test_prompt_templates_api.py`

---
