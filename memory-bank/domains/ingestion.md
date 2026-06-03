# 采集域（Ingestion）

> WARM — RSS 抓取、清洗、去重。改采集逻辑前阅读。

---

## 职责

- 按信源拉取 RSS，解析为统一条目
- URL 去重后写入 `articles`
- 更新 `feed_sources.last_fetched_at`

## 关键代码

| 文件 | 作用 |
|------|------|
| `backend/app/services/ingestion/service.py` | `IngestionService`：单源/全量抓取 |
| `backend/app/services/ingestion/rss_client.py` | HTTP 拉取与解析 |
| `backend/app/services/ingestion/url_utils.py` | URL 规范化、`dedup_key` |
| `backend/app/services/ingestion/seed.py` | 种子信源（汽车/科技/军事） |
| `backend/app/workers/tasks.py` | `fetch_all_feeds` Celery 任务 |

## 数据写入

| 字段 | 来源 |
|------|------|
| `title`, `url`, `published_at` | RSS entry |
| `summary_raw` | RSS 摘要 |
| `content_md` | MVP 通常为空（无 Jina） |
| `fetched_at` | 入库时刻（UTC） |
| `status` | 新建为 `pending` |
| `dedup_key` | 由 URL 派生，配合 `url` 唯一约束去重 |

## 调度

- Beat：`fetch_all_feeds`，周期 `FETCH_INTERVAL_MINUTES`（默认 480）
- 单源 `fetch_interval_minutes`：0 表示跟随全局
- 手动：`POST /api/v1/feed-sources/{id}/fetch`、`POST /tasks/fetch-all`

## 抓取后链式行为

`fetch_all_feeds` 在入库后会调用 `ExtractionService.extract_pending(limit=30)`（见 `tasks.py`），不属于 ingestion 包内逻辑，但属同一 Beat 周期主路径。

## 失败与跳过

- 重复 URL：计为 skipped，不插入
-  inactive 信源：`fetch_all_active` 跳过

## 测试

`test_ingestion_service.py`、`test_rss_parser.py`、`test_url_utils.py`、`test_ingestion_integration.py`（integration 标记）
