# 项目术语表

> COLD — 专有名词与缩写，防止理解偏差。

---

## 业务术语

| 术语 | 英文 | 含义 | 备注 |
|------|------|------|------|
| 板块 | Tag | 垂直领域分类（汽车、科技、军事等） | 对应表 `tags` |
| 信源 | Feed Source | 一条 RSS 订阅配置 | `feed_sources`，归属一个 tag |
| 文章 | Article | 从 RSS 抓取并入库的单条新闻 | `articles` |
| 提炼 / Insight | Article Insight | DeepSeek 生成的结构化摘要与短讯 Markdown | `article_insights` |
| 板块简报 | Tag Brief | 某 tag 在时间窗内的 Markdown 汇总报告 | `tag_briefs.content_md` |
| 简报项 | Tag Brief Item | 简报内引用的文章及排序 | `tag_brief_items` |
| Prompt 模板 | Prompt Template | 提炼用的 system/user 模板 | 可绑定到 tag |

---

## 技术术语

| 术语 | 缩写 | 含义 | 备注 |
|------|------|------|------|
| 抓取间隔 | — | 全局 RSS 调度周期，默认 480 分钟 | `FETCH_INTERVAL_MINUTES` |
| 简报窗口 | Brief Window | 纳入简报的文章时间范围，默认 8 小时 | `BRIEF_WINDOW_HOURS`；过滤字段为 `fetched_at` |
| ApiResponse | — | 统一 API 包装 `{ code, message, data }` | `backend/app/core/response.py` |
| 链式提炼 | — | `fetch_all_feeds` 任务末尾自动 `extract_pending` | limit 30 |

---

## 命名约定

| 前缀/后缀 | 含义 | 示例 |
|-----------|------|------|
| `*`Service | 后端业务逻辑层（同步 Session） | `IngestionService`, `BriefingService` |
| `/kebab-case` | HTTP 路径 | `/feed-sources`, `/tag-briefs` |
| `snake_case` | Python 模块、表名、字段 | `tag_briefs`, `fetch_interval_minutes` |
