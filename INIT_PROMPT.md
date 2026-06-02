# INIT_PROMPT.md — 会话启动模板

> **使用方式**：根据你的场景复制对应的模板，将 `{{PLACEHOLDER}}` 替换为实际内容后，粘贴到 IDE 对话框中。
>
> **前置条件**：确保已按照 README.md 中的步骤 2 激活了 runtime 模板（将 `.template.md` 复制为 `.md`）。

---

## 模式 E：Memory-Bank 模板激活（首次使用必做）

如果还没有将 `.template.md` 复制为正式文件，可以先让 Agent 帮你做：

```
你好，请帮我激活 memory-bank 的 runtime 模板文件：

1. 将 memory_bank/ 下的所有 .template.md 文件复制为对应的 .md 文件：
   - progress.template.md → progress.md
   - decisions.template.md → decisions.md
   - known-issues.template.md → known-issues.md
   - glossary.template.md → glossary.md
2. 完成复制后告诉我，我们开始正式工作。
```

---

## 模式 A：全新项目初始化（Agent 填充所有文档）

```
你好，我们将开始一个新项目。

【项目目标】
{{用1-2句话描述项目要解决什么问题，面向什么用户}}

【技术栈偏好】
{{例如：Vue3 + FastAPI + PostgreSQL，或其他}}

【核心卖点 / 差异化特性】
{{例如：支持自然语言输入记账}}

请按以下步骤操作：

1. 读取 memory-bank 目录下的所有文件模板，理解这套工作规范。
2. 作为架构师，帮我填充 project-brief.md（核心愿景、受众、功能边界）。
3. 草拟 architecture.md（整体技术栈、顶层目录结构、前后端交互宏观流程）。
4. 设计第一版 data-contracts.md（核心数据库表结构 ER 图、核心 API 的请求/响应格式）。
5. 完成这些文档的初始化后，告诉我，我们再开始写第一行代码。
```

---

## 模式 B：已有项目续接（Agent 读取已有文档并审查）

```
你好，这是一个已有项目。请按以下步骤操作：

1. 读取 memory-bank 目录下的所有文件（按照 AGENT_RULES.md 中定义的温度等级加载）。
2. 审查现有文档的完整性和一致性，告诉我：
   - 哪些文档信息不足或过时
   - architecture.md 与实际代码结构是否一致
   - data-contracts.md 的约束是否仍然有效
3. 阅读 progress.md，了解项目历史和当前状态。
4. 阅读 active-task.md，理解当前正在进行的任务。
5. 给出你的审查意见，然后我们继续推进 {{具体的下一步任务}}。
```

---

## 模式 C：单任务突击（跳过审查，直接执行）

```
你好，请按以下步骤操作：

1. 读取 memory-bank 的 HOT 文件（project-brief, architecture, data-contracts, conventions, active-task, progress）。
2. 理解当前项目状态后，直接开始执行任务：
   {{具体任务描述}}
3. 执行完成后，按照 AGENT_RULES.md 的 Update Phase 更新相关文档。
```

---

## 模式 D：架构决策讨论（聚焦决策层面）

```
你好，我们需要做一个架构决策。

【背景】
{{简要描述当前遇到的架构问题或需要决策的事项}}

请按以下步骤操作：

1. 读取 memory-bank 的 HOT 文件和 decisions.md，了解现有架构和已有决策。
2. 给出 2-3 个可行方案，并分析各自优缺点。
3. 给出你的推荐方案及理由。
4. 待我确认后，将最终决策追加到 decisions.md。
```

---

## 自定义提示

你可以根据实际需要，组合以上模板或自行编写 INIT_PROMPT。核心原则是：

- **始终让 Agent 先读 memory-bank**，无论是初始化还是续接
- **明确告诉 Agent 你期望的输出**，是填充文档还是写代码
- **约定好会话结束时的交付物**，让 Agent 知道什么时候算"完成"
