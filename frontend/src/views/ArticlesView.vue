<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { api, unwrap } from "../api/client";
import type { Article } from "../api/types";

const loading = ref(false);
const articles = ref<Article[]>([]);
const status = ref<string>("");

async function load() {
  loading.value = true;
  try {
    const params: Record<string, string> = {};
    if (status.value) params.status = status.value;
    const data = await unwrap<{ items: Article[] }>(
      api.get("/api/v1/articles", { params })
    );
    articles.value = data.items;
  } catch (e) {
    ElMessage.error((e as Error).message);
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <el-card>
    <template #header>
      <div class="row">
        <span>文章库</span>
        <el-space>
          <el-select v-model="status" placeholder="状态" clearable style="width: 140px" @change="load">
            <el-option label="pending" value="pending" />
            <el-option label="extracted" value="extracted" />
            <el-option label="failed" value="failed" />
          </el-select>
          <el-button size="small" @click="load">刷新</el-button>
        </el-space>
      </div>
    </template>
    <el-table v-loading="loading" :data="articles" stripe>
      <el-table-column prop="title" label="标题" min-width="240" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column prop="fetched_at" label="抓取时间" width="180" />
      <el-table-column label="链接" width="80">
        <template #default="{ row }">
          <el-link :href="row.url" target="_blank" type="primary">原文</el-link>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<style scoped>
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
