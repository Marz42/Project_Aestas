# 测试指南

> COLD — 编写或运行测试时读取。

---

## 测试框架与工具

| 层级 | 工具 | 状态 |
|------|------|------|
| 后端 | pytest + pytest-asyncio + httpx | 已使用 |
| 前端 | Vitest + Vue Test Utils | **M4 未配置** |

规范详见 `memory-bank/conventions.md` 测试节。

---

## 运行命令

在 **`Project_Aestas/backend`** 目录（避免 PYTHONPATH 指向其他仓库）：

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q -m "not integration"    # 单元测试（默认）
pytest -q -m integration          # 需 Postgres，真实拉取 RSS
pytest -q                         # 全部
```

集成测试需本地或 Docker 提供 Postgres，并配置与 `.env.example` 一致的 `DATABASE_URL`。

---

## 测试模块一览（`backend/tests/`）

| 文件 | 覆盖 |
|------|------|
| `test_health.py` | `/health` |
| `test_feed_sources_api.py` | 信源 API |
| `test_tag_briefs_api.py` | 简报 API |
| `test_prompt_templates_api.py` | Prompt CRUD |
| `test_ingestion_service.py` | 采集服务 |
| `test_ingestion_integration.py` | RSS 集成（integration） |
| `test_ingestion_long_url.py` | 长 URL |
| `test_rss_parser.py` | RSS 解析 |
| `test_url_utils.py` | URL 工具 |
| `test_seed.py` | 种子数据 |
| `test_extraction_service.py` | 提炼服务 |
| `test_llm_client.py` | DeepSeek 客户端 |
| `test_extraction_markdown.py` | 短讯 Markdown |
| `test_prompts.py` | Prompt 组装 |
| `test_briefing_service.py` | 简报服务 |
| `test_briefing_markdown.py` | 简报 Markdown |
| `test_workers_m3.py` | Celery 任务行为 |
| `test_time_windows.py` | 时间窗工具 |

---

## 测试规范摘要

- 新功能与 bug 修复须同 PR 交付 pytest
- API 测试断言 `ApiResponse` 的 `code` 与 `data`
- Bug 修复：先写失败用例再修
- 不为覆盖率写无意义断言

---

## 前端测试（后续）

引入 Vitest 后，建议与 `frontend/src/views/` 同目录或 `__tests__/` 放置 `*.test.ts`。
