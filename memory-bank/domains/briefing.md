# 简报域（Briefing）

> WARM — 板块 Markdown 汇总。改简报规则前阅读。

---

## 职责

- 按 tag 聚合时间窗内已提炼文章
- 生成 `tag_briefs.content_md` 与 `tag_brief_items` 关联
- 保证 `(tag_id, window_start)` 幂等

## 关键代码

| 文件 | 作用 |
|------|------|
| `backend/app/services/briefing/service.py` | `BriefingService` |
| `backend/app/services/briefing/markdown.py` | `render_tag_brief_md` |
| `backend/app/core/time_windows.py` | `current_brief_window()` |
| `backend/app/workers/tasks.py` | `generate_tag_briefs` |
| `backend/app/api/v1/tag_briefs.py` | 查询、下载、手动 generate |

## 时间窗

- 默认：`window_end = now(UTC)`，`window_start = now - BRIEF_WINDOW_HOURS`（8）
- 纳入条件：`Article.fetched_at >= window_start` 且 `< window_end`，`status == extracted`
- 排序：按 `fetched_at` 降序

## 幂等

已存在同 `(tag_id, window_start)` 的 `TagBrief` 且 `force=False` 时直接返回已有记录及 `item_count`。

`force=True` 时删除旧简报后重建。

## 输出

- `tag_briefs.status`：新建默认为 `generated`
- `content_md`：板块标题、窗口、每条 insight 卡片（标题、摘要、要点、原文链接）
- 下载：`GET /tag-briefs/{id}/download` → `text/markdown`

## 调度与手动

- Beat：`generate_tag_briefs`，周期与 fetch 相同（8h）
- 手动：`POST /tasks/generate-briefs`、`POST /tag-briefs/generate`（可指定 `tag_id`）

## 测试

`test_briefing_service.py`、`test_briefing_markdown.py`、`test_tag_briefs_api.py`、`test_workers_m3.py`
