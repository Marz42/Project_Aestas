<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { api, unwrap } from "../api/client";
import type { FeedSource } from "../api/types";

const loading = ref(false);
const feeds = ref<FeedSource[]>([]);

async function load() {
  loading.value = true;
  try {
    const data = await unwrap<{ items: FeedSource[] }>(api.get("/api/v1/feed-sources"));
    feeds.value = data.items;
  } catch (e) {
    ElMessage.error((e as Error).message);
  } finally {
    loading.value = false;
  }
}

async function fetchOne(id: string) {
  try {
    await unwrap(api.post(`/api/v1/feed-sources/${id}/fetch`));
    ElMessage.success("抓取完成");
    await load();
  } catch (e) {
    ElMessage.error((e as Error).message);
  }
}

onMounted(load);
</script>

<template>
  <el-card>
    <template #header>
      <div class="row">
        <span>RSS 信源</span>
        <el-button size="small" @click="load">刷新</el-button>
      </div>
    </template>
    <el-table v-loading="loading" :data="feeds" stripe>
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="feed_url" label="URL" min-width="280" />
      <el-table-column prop="is_active" label="启用" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? "是" : "否" }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="fetchOne(row.id)">抓取</el-button>
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
