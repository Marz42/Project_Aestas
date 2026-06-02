<script setup lang="ts">
import { ref } from "vue";
import { ElMessage } from "element-plus";
import { api, unwrap } from "../api/client";

const loading = ref(false);

async function runTask(path: string, label: string) {
  loading.value = true;
  try {
    await unwrap(api.post(path));
    ElMessage.success(`${label} 已触发`);
  } catch (e) {
    ElMessage.error((e as Error).message);
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <el-card>
    <template #header>快捷任务</template>
    <el-space wrap>
      <el-button :loading="loading" @click="runTask('/api/v1/tasks/seed-feeds', '种子信源')">
        初始化信源
      </el-button>
      <el-button :loading="loading" @click="runTask('/api/v1/tasks/seed-prompts', '种子 Prompt')">
        初始化 Prompt
      </el-button>
      <el-button :loading="loading" type="primary" @click="runTask('/api/v1/tasks/fetch-all', '抓取')">
        抓取 RSS
      </el-button>
      <el-button :loading="loading" @click="runTask('/api/v1/tasks/extract-pending', '提炼')">
        AI 提炼
      </el-button>
      <el-button :loading="loading" @click="runTask('/api/v1/tasks/generate-briefs', '简报')">
        生成简报
      </el-button>
    </el-space>
    <p class="hint">建议顺序：初始化 → 抓取 → 提炼 → 生成简报。API Key 在 frontend/.env 配置。</p>
  </el-card>
</template>

<style scoped>
.hint {
  margin-top: 16px;
  color: #6b7280;
  font-size: 13px;
}
</style>
