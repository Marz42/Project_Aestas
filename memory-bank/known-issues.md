# 已知问题与调试心得

> COLD — 排查 Bug 或诡异行为时读取。

---

## 问题记录

### development 环境可省略 X-API-Key

**症状**: 本地 curl 不带 `X-API-Key` 仍返回 200。  
**根因**: `verify_api_key` 在 `environment=development` 且未提供头时直接放行。  
**解决方案**: 生产部署将 `ENVIRONMENT` 设为非 `development`；测试鉴权时显式传错误 Key 验证 401。  
**发现日期**: 2026-06-03  
**关联 ADR**: —

---

### pytest 导入错误 app 来自其他仓库

**症状**: `ImportError: cannot import name 'check_sync_db' from 'app.core.database'`，路径指向非本仓库（如其他项目的 `backend`）。  
**根因**: `PYTHONPATH` 或当前工作目录指向错误项目。  
**解决方案**: `cd Project_Aestas/backend` 后执行 `pytest -q`；确认 venv 为本项目 `.venv`。  
**发现日期**: 2026-06-03  
**关联 ADR**: —

---

### 文档曾描述但未实现的能力

**症状**: Agent 或新人假设已有 Jina 全文、`reports/` 目录导出、飞书/企微推送。  
**根因**: `project-brief` / `architecture` 早期写为「可选」或 P2，代码未实现。  
**解决方案**: 以 `memory-bank/architecture.md`「未实现」节为准；需要时走 M5 或单独 ADR。  
**发现日期**: 2026-06-03  
**关联 ADR**: ADR-005

---

### deepseek-v4-flash 与 Instructor 默认 tool_choice 冲突

**症状**: `extract-pending` 全部 `failed`，日志 `Thinking mode does not support this tool_choice`。  
**根因**: V4 模型默认 thinking 模式，Instructor 结构化输出会发送 `tool_choice=required`。  
**解决方案**: `llm_client.completion_extra_body()` 对含 `v4` 的模型传入 `extra_body={"thinking": {"type": "disabled"}}`（见 `backend/app/services/extraction/llm_client.py`）。  
**发现日期**: 2026-06-03  
**关联 ADR**: ADR-004

---

### tag_briefs.status 无 draft 流转

**症状**: 契约枚举含 `draft`，库中新建简报直接为 `generated`。  
**根因**: MVP 实现未引入草稿态。  
**解决方案**: 调用方以 `generated` / `failed` 为准；若需草稿再开 ADR。  
**发现日期**: 2026-06-03  
**关联 ADR**: —
