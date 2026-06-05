# 简报域（Briefing）

> WARM — 板块 Markdown 汇总。改简报规则前阅读。

---

## 职责

- 按 tag + 时间窗聚合内容，生成 `tag_briefs`
- M4：按**文章**逐条写入 `content_md`
- M5c：按**事件 cluster** 一节 + **周期导语** + 多链接

## 关键代码

| 文件 | 作用 |
|------|------|
| `backend/app/services/briefing/service.py` | `BriefingService` |
| `backend/app/services/briefing/markdown.py` | Markdown 渲染 |
| `backend/app/core/time_windows.py` | `current_brief_window()` |
| `backend/app/workers/tasks.py` | `generate_tag_briefs` |

## 时间窗

`window_end = now(UTC)`，`window_start = now - BRIEF_WINDOW_HOURS`（8）

## M5c 简报形态（已确认）

1. **本期综述**（`intro_md`）：本周期、本板块内所有事件的**整体中文总结**（独立 Prompt，`purpose=briefing_intro`，后台可编辑）
2. **事件节**（每个 `story_cluster` 一节）：
   - 事件标题 + 合并摘要
   - **报道来源**：多条原文链接（BBC、TWZ、CNN…）
3. 统计行：事件数 + 报道篇数

流水线顺序（M5 目标）：`fetch` → `extract` → **`cluster`** → `generate_tag_briefs`

## 幂等

`(tag_id, window_start)` 唯一；`force=True` 时删除重建。

## 当前实现（M4）

- 纳入：`fetched_at` 在窗内且 `status=extracted` 的 articles
- `content_md` 按文章编号，单链接

## 测试

`test_briefing_service.py`、`test_briefing_markdown.py`、`test_tag_briefs_api.py`

---
