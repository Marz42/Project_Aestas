# 数据契约

> 🔥 HOT — 数据库表结构与核心 API 格式。改表或改公共 API 前须与用户确认。

---

# 全局配置常量（代码 / 环境变量）

| 名称 | 默认值 | 说明 |
|------|--------|------|
| `FETCH_INTERVAL_MINUTES` | `480` | RSS 抓取间隔（8 小时） |
| `BRIEF_WINDOW_HOURS` | `8` | 简报聚合时间窗（小时） |
| `DEEPSEEK_API_KEY` | — | 必填（实现 AI 时），仅环境变量 |
| `DEEPSEEK_MODEL` | `deepseek-chat` | DeepSeek 模型名 |

---

# 通用 API 响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

| code | 含义 |
|------|------|
| 200 | 成功 |
| 400 | 参数错误 |
| 401 | 未认证 |
| 404 | 不存在 |
| 500 | 服务器错误 |

分页 `data`：`{ "items": [], "total": 0, "page": 1, "page_size": 20 }`

---

# 数据库 ER（MVP）

> `delivery_targets` 已移出 MVP，见文末 P2。

```mermaid
erDiagram
    tags ||--o{ feed_sources : has
    tags ||--o{ articles : classifies
    tags ||--o{ tag_briefs : owns
    feed_sources ||--o{ articles : produces
    articles ||--o| article_insights : yields
    tag_briefs ||--o{ tag_brief_items : contains
    articles ||--o{ tag_brief_items : referenced_by
    prompt_templates ||--o{ tags : optional_default

    tags {
        uuid id PK
        string slug UK
        string name
        uuid prompt_template_id FK
    }

    feed_sources {
        uuid id PK
        uuid tag_id FK
        string name
        string feed_url
        int fetch_interval_minutes
        bool is_active
        timestamptz last_fetched_at
    }

    articles {
        uuid id PK
        uuid feed_source_id FK
        uuid tag_id FK
        string title
        string url UK
        text content_md
        timestamptz published_at
        timestamptz fetched_at
        string status
        string dedup_key
    }

    article_insights {
        uuid id PK
        uuid article_id FK UK
        jsonb structured
        text short_news_md
        timestamptz processed_at
    }

    tag_briefs {
        uuid id PK
        uuid tag_id FK
        timestamptz window_start
        timestamptz window_end
        string title
        text content_md
        string status
        timestamptz generated_at
    }

    tag_brief_items {
        uuid id PK
        uuid tag_brief_id FK
        uuid article_id FK
        int sort_order
    }

    prompt_templates {
        uuid id PK
        string name
        string purpose
        text system_prompt
        text user_prompt_template
    }
```

---

# 表字段说明

## `feed_sources`

| 字段 | 说明 |
|------|------|
| `fetch_interval_minutes` | 默认 **480**；单源可覆盖，0 表示跟随全局 |
| `source_type` | MVP：`rss` |

## `articles`

| `status` | 含义 |
|----------|------|
| `pending` | 待 DeepSeek 提炼 |
| `extracted` | 已有 `article_insights` |
| `skipped` / `failed` | 跳过或失败 |

## `article_insights` — DeepSeek 结构化输出

```json
{
  "headline": "一句话标题",
  "summary": "2-3 句摘要",
  "key_facts": ["事实 1"],
  "why_it_matters": "行业影响",
  "source_url": "与 articles.url 一致"
}
```

`short_news_md`：单条 Markdown 卡片。

## `tag_briefs` — 板块 Markdown 简报

| 字段 | 说明 |
|------|------|
| `window_start` / `window_end` | 8 小时窗口（UTC 存储） |
| `content_md` | **MVP 主交付物**：完整 Markdown 报告 |
| `status` | `draft` → `generated` → `failed` |

唯一约束：`(tag_id, window_start)`。

**简报纳入规则**：`articles.fetched_at`（或 `published_at`，实现时二选一并写死）∈ `[window_start, window_end)` 且对应文章 `status = extracted`。

## `tag_briefs.content_md` 结构建议

```markdown
# {tag_name} 简报 · {window_start} — {window_end} (UTC)

> 共 N 条 · 由 Project Aestas 自动生成

## 1. {headline}
{summary}
**要点**: ...
**原文**: {url}

---
...
```

---

# 核心 API（v1）

Base: `/api/v1` · 认证：`X-API-Key`

## Tags / Feed Sources / Articles

（与上一版相同，略）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/tags` | 列表 |
| POST | `/tags` | 创建 |
| GET/POST/PATCH | `/feed-sources` | CRUD；创建时 `fetch_interval_minutes` 默认 480 |
| POST | `/feed-sources/{id}/fetch` | 手动抓取 |
| GET | `/articles` | `tag_id`, `status`, `from`, `to` |
| GET | `/articles/{id}` | 含 insight |
| POST | `/articles/{id}/reextract` | 重新调用 DeepSeek |

## Tag Briefs（原 daily-briefs，更名对齐表名）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/tag-briefs` | `?tag_id=&window_start=` |
| GET | `/tag-briefs/{id}` | 返回含 `content_md` |
| GET | `/tag-briefs/{id}/download` | `Content-Type: text/markdown` 附件 |
| POST | `/tag-briefs/generate` | `{ "tag_id" }` 或指定 `window_start`；默认最近 8h |

**响应 data 示例**

```json
{
  "id": "uuid",
  "tag_id": "uuid",
  "tag_name": "汽车",
  "window_start": "2026-06-02T00:00:00Z",
  "window_end": "2026-06-02T08:00:00Z",
  "title": "汽车板块简报",
  "content_md": "# 汽车板块简报\n\n...",
  "status": "generated",
  "item_count": 12
}
```

## Tasks

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/tasks/fetch-all` | 手动全量抓取 |
| POST | `/tasks/generate-briefs` | 手动生成各 tag 简报 |
| GET | `/health` | `{"status":"ok"}` 无包装 |

---

# P2 预留（不在 MVP 实现）

### `delivery_targets`

| channel_type | 说明 |
|--------------|------|
| `feishu_webhook` | 飞书 |
| `wecom_webhook` | 企微 |

### 已移除的 MVP 端点

- `POST /tag-briefs/{id}/deliver` — 推送后置

---

# 枚举

```python
# articles.status
pending | extracted | skipped | failed

# tag_briefs.status
draft | generated | failed
```

---

# 变更记录

| 日期 | 变更 |
|------|------|
| 2026-06-02 | 初版 ER + API |
| 2026-06-02 | DeepSeek；8h 抓取/简报窗；`tag_briefs`；移除 MVP 推送 |

---
