# 当前焦点

> HOT — 同一时间只推进一个主题。

---

## 当前阶段：M5b-2 已编码（待 Docker 迁移与 E2E）

### 已完成

- [x] pgvector 镜像、`005` 迁移（taxonomy、content_tags、embedding）
- [x] 提炼 `content_tags` 1~3 + Prompt 注入标签池
- [x] `seed-taxonomy`、extract 后 bge-m3 embed、`embed-pending`
- [x] ANN `content_tags &&` + bge-reranker + 增量门禁聚类
- [x] `CLUSTERING_MODE=vector|llm`；`cluster_title` LLM 润色
- [x] 简报按成员 tag / content_tags 交集纳入 cluster
- [x] 控制台：标签池、补向量、向量/LLM 聚类

### 本地验收步骤

```powershell
docker compose up -d --build
docker compose exec api alembic upgrade head
# API：seed-taxonomy → seed-prompts → reextract 或 extract-pending → embed-pending → cluster-briefs → generate-briefs
```

历史文章需 **reextract**（补 content_tags）再 **embed-pending**。

### 配置（`backend/.env` 可选）

- `CLUSTERING_MODE=vector`（默认）
- `RERANK_PAIR_THRESHOLD=0.85`
- `RERANK_CLUSTER_AVG_MIN=0.80`

---
