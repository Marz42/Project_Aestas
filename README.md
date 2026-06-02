# Project Paradigma

*Vibe Coding 时代的项目开发基座*

## 核心理念

本项目是一个 **IDE 无关的项目开发基座**，核心是一套 "Memory-Bank" 外部记忆系统。
它的目标是解决 LLM 辅助编程中的三个核心痛点：

- **上下文腐化** — 会话变长后，Agent 逐渐遗忘早期的约定和决策
- **注意力涣散** — Token 窗口塞入过多细节时，Agent 对架构约束的注意力被稀释
- **会话间不连续性** — 每次新建对话时 Agent 从零开始，无法继承之前的上下文

通过将关键信息外化到结构化的文件中，Memory-Bank 确保 Agent 每次都能快速"上车"。

---

## 如何使用 / How To Use

### 1. 克隆本项目作为开发基座

```bash
git clone <repo-url> my-new-project
cd my-new-project
```

### 2. 激活 runtime 模板（重要！）

本项目只跟踪 `.template.md` 模板文件。实际使用时，需要将模板复制为正式文件：

```bash
# 在 memory_bank/ 目录下执行
cp progress.template.md progress.md
cp decisions.template.md decisions.md
cp known-issues.template.md known-issues.md
cp glossary.template.md glossary.md
```

> **为什么这样设计？** 包含本项目开发历史的 `progress.md`、`decisions.md` 等运行时数据已通过 `.gitignore` 排除。
> 你 clone 到的永远是一套干净的模板，不会带有上游项目的开发历史。

### 3. 配置 IDE 适配器

本项目已内置 Cursor 的 Rule 适配器（`.cursor/rules/memory-bank-protocol.mdc`）。

如果你使用其他 IDE（Codex、Antigravity 等），请根据 `AGENT_RULES.md`（IDE 无关的协议原文）自行创建对应的规则文件。

### 4. 启动第一个会话

打开 `INIT_PROMPT.md`，根据你的场景选择对应的模板（模式 A：全新项目 / 模式 B：已有项目续接 / 模式 C：单任务突击 / 模式 D：架构决策讨论），将 `{{PLACEHOLDER}}` 替换后粘贴到 IDE 对话框中。

---

## 文件温度体系

Memory-Bank 内的文件按使用频率分为三个温度等级：

| 温度 | 含义 | 图标 | 加载策略 |
|------|------|------|----------|
| 🔥 HOT | 每次对话必读 | 🔥 | Agent 启动时主动读取 |
| 🌡️ WARM | 按需加载 | 🌡️ | 涉及相关模块时才读取 |
| 🧊 COLD | 仅排查时读 | 🧊 | 遇到决策疑问或 Bug 时自行判断 |

---

## 完整目录结构

```
paradigma/
├── 📄 README.md                              # 本文件
├── 📄 AGENT_RULES.md                         # 【源头】IDE 无关的协议原文
├── 📄 INIT_PROMPT.md                         # 【入口】多模式会话启动模板
├── 📁 .cursor/rules/
│   └── 📄 memory-bank-protocol.mdc           # 【Cursor适配器】自动加载的规则文件
│
└── 📁 memory_bank/
    │
    ├── 🔥 HOT — 每次对话必读 ─────────────────────
    ├── 📄 project-brief.md                   # 【定海神针】项目愿景、核心受众、功能边界
    ├── 📄 architecture.md                    # 【系统蓝图】技术栈、顶层目录结构、前后端交互
    ├── 📄 data-contracts.md                  # 【最高法律】数据库表结构、API 请求/响应格式
    ├── 📄 conventions.md                     # 【肌肉记忆】代码规范、命名约定、错误处理规范
    ├── 📄 active-task.md                     # 【当前焦点】正在执行的单个任务（Check-list 格式）
    ├── 📄 progress.md                        # 【会话日志】历次会话摘要（gitignored — 从 progress.template.md 复制）
    ├── 📄 progress.template.md               #   (跟踪 — 复制为 progress.md 使用)
    │
    ├── 🌡️ WARM — 按需加载 ─────────────────────
    ├── 📄 roadmap.md                         # 【宏观进度】已完成版本、当前目标、未来规划
    ├── 📁 domains/                           # 【领域拆分】按模块拆分的设计文档
    │   └── 📄 module_1.md                    #    (示例模块，按需创建更多)
    │
    └── 🧊 COLD — 排查时读取（.template.md 供复制，.md 由 .gitignore 排除）──
        ├── 📄 decisions.template.md          # 【架构决策】ADR 模板（复制为 decisions.md 使用）
        ├── 📄 known-issues.template.md       # 【已知坑位】问题记录模板（复制为 known-issues.md 使用）
        ├── 📄 glossary.template.md           # 【术语表】术语录入模板（复制为 glossary.md 使用）
        ├── 📄 decisions.md                   #   (gitignored — 你的项目实际决策记录)
        ├── 📄 known-issues.md                #   (gitignored — 你的项目实际坑位记录)
        ├── 📄 glossary.md                    #   (gitignored — 你的项目实际术语表)
        └── 📁 manuals/                       # 【操作手册】部署运维与测试指南（模板，直接使用）
            ├── 📄 deploy.md                  #   部署与运维指南
            └── 📄 testing-guide.md           #   测试用例编写规范与测试账号
```

---

## IDE 生态整合

本项目通过"一个源头 + 多个适配器"的策略适配不同 IDE：

| 整合层级 | 文件 | IDE 支持 | 作用 |
|----------|------|----------|------|
| **Rule 层** | `.cursor/rules/memory-bank-protocol.mdc` | Cursor | 每个新会话自动加载协议 |
| **用户入口层** | `INIT_PROMPT.md` | 所有 IDE | 用户手动复制粘贴，控制 Agent 起始任务方向 |
| **协议源头** | `AGENT_RULES.md` | 所有 IDE | IDE 无关的规范原文，各适配器的同步依据 |

### 如何为新 IDE 创建适配器

1. 阅读 `AGENT_RULES.md` 了解完整协议
2. 在你的 IDE 中创建对应的规则/自定义指令文件
3. 将核心协议（温度体系 + 四阶段工作流）提取到适配器文件中
4. 确保适配器与本项目 `AGENT_RULES.md` 保持同步更新

---

## 维护原则

1. **先改源头，后改适配器**：协议变更先更新 `AGENT_RULES.md`，再同步到各 IDE 适配器
2. **冷热分离，不堆砌**：新增文档时明确其温度等级，避免 HOT 层过重导致 Agent 注意力涣散
3. **实战驱动，持续迭代**：Memory-Bank 的内容应在实际项目中持续维护和演进，而不是一次性填满
4. **模板与运行时分离**：
   - 会累积项目特定数据的文件（progress, decisions, known-issues, glossary）使用 `.template.md` → `.md` 复制模式
   - `.template.md` 进 git，`.md` 由 `.gitignore` 排除
   - 纯模板/规范文件（conventions.md, project-brief.md 等）直接跟踪，不需要 `.template` 机制
   - 如果某个文件同时包含"模板结构"和"本项目开发历史"，应拆分为 template + runtime
