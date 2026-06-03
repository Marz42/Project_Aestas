# 会话进度日志

> HOT — 记录每次 Agent 会话的摘要。每次对话开始时读取，了解项目历史。

---

## 会话记录

### 2026-06-02 - M1–M4 里程碑交付

**完成事项**:

- [x] M1：docker-compose（postgres/redis/api/worker/beat）、FastAPI `/health`、`ApiResponse`、Alembic 初始表、Celery Beat 冒烟
- [x] M2：RSS 8h 抓取、URL 去重、`feed-sources` API、种子信源（汽车/科技/军事）
- [x] M3：DeepSeek + Instructor 提炼、`tag_briefs` Markdown 简报、下载 API、端到端流水线
- [x] M4：Vue 3 管理后台（控制台/信源/文章/简报/Prompt）、`prompt_templates` CRUD、板块绑定 Prompt、Docker `admin` 服务

**踩坑记录**:

- 模板仓库 `.gitignore` 默认忽略 `progress.md` 等运行时文件，clone 后需解除忽略才能纳入版本库。

**遗留问题**:

- [ ] 端到端验证简报质量，按需微调 Prompt
- [ ] M5：飞书/企微推送、去重优化（未开始）

**下一步建议**:

- 在 Docker 环境跑一轮 `seed-feeds` → `fetch-all` → `generate-briefs`，人工审阅 `content_md`

---

### 2026-06-03 - Memory-bank 目录统一与文档对齐

**完成事项**:

- [x] `memory_bank/` 重命名为 `memory-bank/`，与 `AGENT_RULES.md` 一致
- [x] 移除 `.gitignore` 对 progress/decisions/known-issues/glossary 的屏蔽
- [x] 新建并填充 COLD 文档（decisions、known-issues、glossary、progress）
- [x] 更新 HOT/WARM 文档与代码对齐；新增 `domains/` 三份模块说明
- [x] 补齐 `manuals/deploy.md`、`manuals/testing-guide.md`

**踩坑记录**:

- 无（文档变更）

**遗留问题**:

- [ ] 同 2026-06-02 条目

**下一步建议**:

- 用户确认后进入 E2E 简报验证或 M5 选型

---

### 2026-06-03 - E2E 验证（BBC + TWZ，deepseek-v4-flash）

**完成事项**:

- [x] Docker Compose 全栈；`.env` 使用 `deepseek-v4-flash`
- [x] 仅启用 BBC、TWZ 信源；72 条提炼成功；军事简报 34 条、科技简报 38 条
- [x] 修复 V4 thinking 与 Instructor 冲突（`llm_client.completion_extra_body`）

**踩坑记录**:

- 无 Key 时提炼全失败；V4 默认 thinking 导致 `tool_choice` 400（已修复）

**遗留问题**:

- [ ] Prompt 语言统一（部分中英混排）
- [ ] M5 / 恢复其他信源

**下一步建议**:

- 在 http://localhost:5173 预览完整简报；满意后进入 M5 或 Prompt 微调
