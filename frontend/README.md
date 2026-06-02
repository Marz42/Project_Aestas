# Aestas Admin (Vue 3)

## 开发

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_KEY 需与 backend/.env 的 API_KEY 一致
npm run dev
```

打开 http://localhost:5173（API 通过 Vite 代理到 `localhost:8000`）。

## Docker

随根目录 `deploy/docker-compose.yml` 启动后访问 http://localhost:5173

## 功能

- **控制台**：一键触发抓取 / 提炼 / 简报
- **信源 / 文章 / 简报**：列表与预览
- **Prompt**：新建、编辑、删除；为各板块选择已保存的 Prompt 模板
