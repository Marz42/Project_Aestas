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

---

### 2026-06-03 - M5 路线确认（文档更新，待实施）

**完成事项**:

- [x] 与用户确认 M5 范围：M5a 中文 Prompt（**全部 Prompt 前台可编辑**）→ M5b 同板块聚类（**先 LLM，后本地 embedding+pgvector**）→ M5c 简报（**导语+一事件一节多链接**）
- [x] 推送移出 M5；URL 去重保留、不做标题去重替代聚类
- [x] 更新 `roadmap.md`、`active-task.md`、`data-contracts.md`（M5 计划契约）、`decisions.md`（ADR-007–010）、`domains/clustering.md` 等

**踩坑记录**:

- 无

**遗留问题**:

- [ ] 用户确认后开始 M5a 编码

**下一步建议**:

- 用户回复「开始实施」后从 M5a 动手

---

### 2026-06-03 - M5 实施（M5a / M5b-1 / M5c）

**完成事项**:

- [x] M5a：中文默认 Prompt、`seed-prompts` 四类模板、schema 中文约束
- [x] M5b-0/1：`story_clusters` 迁移、聚类服务、LLM 分组、`POST /tasks/cluster-briefs`、`GET /story-clusters`
- [x] M5c：`intro_md`、按 cluster 生成简报 Markdown、简报/聚类前台、控制台流水线按钮
- [x] 测试：36 passed（含 `test_clustering_markdown`、`test_briefing_service` mock 更新）
- [x] 前端 `npm run build` 通过

**踩坑记录**:

- `test_clustering_service` 缺 DB fixture，改为仅保留 markdown 单元测试
- `deepseek-v4-flash` 聚类/导语 E2E 尚未在本会话跑通

**遗留问题**:

- [ ] Docker 内 `alembic upgrade head` + 全流水线 E2E
- [ ] M5a 验收：重提炼后简报全中文
- [ ] M5b-2 pgvector（未开始）

**下一步建议**:

- `docker compose up -d --build` → `seed-prompts` → fetch → extract → cluster-briefs → generate-briefs

---

### 2026-06-03 - M5b-2 实施（向量聚类 + 多标签）

**完成事项**:

- [x] Postgres `pgvector/pgvector:pg16`；迁移 `005`（taxonomy、content_tags、embedding HNSW）
- [x] 提炼输出 `content_tags` 1~3；`seed-taxonomy`；extract 后 bge-m3 向量化
- [x] ANN `content_tags &&` + bge-reranker-v2-m3 + 增量归属（pair≥0.85 & avg≥0.80）
- [x] `CLUSTERING_MODE=vector|llm`；`cluster_title` LLM 润色；控制台新按钮
- [x] pytest 42 passed（集成测试需 pgvector 镜像迁移后通过）

**下一步**:

- Docker：`alembic upgrade head` → `seed-taxonomy` → 历史文章 reextract → `embed-pending` → `cluster-briefs`
