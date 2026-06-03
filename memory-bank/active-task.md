# 当前焦点

> HOT — 同一时间只推进一个主题。

---

## 当前阶段：M4 完成 · 文档已对齐（2026-06-03）

### Checklist — M4（已完成）

- [x] Vue 3 + Element Plus 管理后台（控制台 / 信源 / 文章 / 简报 / Prompt）
- [x] `prompt_templates` 表与 CRUD API
- [x] 板块绑定 Prompt；DeepSeek 提炼读取自定义模板
- [x] Docker `admin` 服务（:5173）
- [x] pytest 套件（`backend/tests/`，18 个测试模块）

### Checklist — 文档对齐（已完成）

- [x] `memory-bank/` 目录命名统一
- [x] COLD 运行时文档入库（progress / decisions / known-issues / glossary）
- [x] HOT + domains + manuals 与代码同步

### E2E 验证（2026-06-03，已完成）

- [x] BBC + TWZ RSS；`deepseek-v4-flash`；72 条提炼、军事 34 / 科技 38 条简报
- [x] `llm_client` V4 thinking 与 Instructor 兼容修复

### 下一工作包（待启动）

- [ ] 管理后台 http://localhost:5173 完整浏览简报，按需微调 Prompt
- [ ] 恢复/调整其他信源（少数派、联合早报）或保持双源测试
- [ ] M5 选型：飞书 Webhook **或** 去重增强

---
