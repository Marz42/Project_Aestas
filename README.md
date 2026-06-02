# Project Aestas

*垂直领域编辑的 AI 新闻降噪与线索提取工具*

为汽车、科技、军事等不同板块的新闻编辑自动聚合 RSS 信源，用 **DeepSeek** 提炼单条线索，并按板块生成 **Markdown 简报**。

---

## 产品能力（MVP）

| 模块 | 说明 |
|------|------|
| **A. 采集** | 默认每 **8 小时**拉取 RSS，清洗入库（覆盖全球时区发稿节奏） |
| **B. 简报** | DeepSeek 单条提炼 → 按板块聚合为 Markdown 报告 |
| **C. 输出** | 简报写入数据库，经 API 查看/下载；**IM 推送后置** |

详细愿景与边界见 [`memory_bank/project-brief.md`](memory_bank/project-brief.md)。

---

## 技术栈

| 层级 | 选型 |
|------|------|
| 后端 | Python 3.12 · FastAPI · SQLAlchemy · Celery |
| 前端 | Vue 3 · TypeScript · Element Plus（P1 管理后台） |
| 数据 | PostgreSQL · Redis |
| LLM | **DeepSeek**（OpenAI 兼容 API，`DEEPSEEK_API_KEY` 由你在 `.env` 提供） |
| 部署 | Docker Compose |

架构与目录规划：[`memory_bank/architecture.md`](memory_bank/architecture.md)  
表结构与 API：[`memory_bank/data-contracts.md`](memory_bank/data-contracts.md)

---

## 本地开发（M1 起逐步补齐）

```bash
git clone https://github.com/Marz42/Project_Aestas.git
cd Project_Aestas
```

复制环境变量示例（实现代码后提供 `backend/.env.example`）：

```bash
# DeepSeek — 实现 AI 模块时必填
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_MODEL=deepseek-chat

# 调度默认值（与文档一致，可在代码中覆盖）
FETCH_INTERVAL_MINUTES=480   # 8 小时抓取一次
BRIEF_WINDOW_HOURS=8         # 简报覆盖最近 8 小时入库文章
```

启动方式将在 M1 完成后写入 `memory_bank/manuals/deploy.md`。

---

## Memory-Bank（Agent 协作文档）

本项目使用 `memory_bank/` 作为外部记忆，Cursor 会通过 `.cursor/rules/memory-bank-protocol.mdc` 自动加载。

| 温度 | 文件 |
|------|------|
| 🔥 HOT | `project-brief.md` · `architecture.md` · `data-contracts.md` · `conventions.md` · `active-task.md` · `progress.md`（本地，gitignore） |
| 🌡️ WARM | `roadmap.md` |
| 🧊 COLD | `decisions.md` · `known-issues.md` · `glossary.md`（从 `.template.md` 复制，gitignore） |

新会话可从 [`INIT_PROMPT.md`](INIT_PROMPT.md) 选择模式；协议原文见 [`AGENT_RULES.md`](AGENT_RULES.md)。

**首次 clone 后**（若尚未复制运行时模板）：

```bash
cd memory_bank
cp progress.template.md progress.md
cp decisions.template.md decisions.md
cp known-issues.template.md known-issues.md
cp glossary.template.md glossary.md
```

---

## 仓库

- **Remote**：`https://github.com/Marz42/Project_Aestas`
- 由 [Paradigma](https://github.com/Marz42/paradigma) 模板初始化；上游 remote 已断开，独立演进。

---

## 许可证

本项目采用 [MPL 2.0](LICENSE) 协议（继承自开发基座模板）。
