<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { api, unwrap } from "../api/client";
import type { TagBrief } from "../api/types";

const loading = ref(false);
const briefs = ref<TagBrief[]>([]);
const preview = ref("");
const drawer = ref(false);

async function load() {
  loading.value = true;
  try {
    const data = await unwrap<{ items: TagBrief[] }>(api.get("/api/v1/tag-briefs"));
    briefs.value = data.items;
  } catch (e) {
    ElMessage.error((e as Error).message);
  } finally {
    loading.value = false;
  }
}

async function openBrief(row: TagBrief) {
  try {
    const detail = await unwrap<TagBrief>(api.get(`/api/v1/tag-briefs/${row.id}`));
    preview.value = detail.content_md || "";
    drawer.value = true;
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
        <span>板块简报</span>
        <el-button size="small" @click="load">刷新</el-button>
      </div>
    </template>
    <el-table v-loading="loading" :data="briefs" stripe>
      <el-table-column prop="tag_name" label="板块" width="100" />
      <el-table-column prop="title" label="标题" min-width="200" />
      <el-table-column prop="item_count" label="条数" width="80" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="openBrief(row)">预览</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-drawer v-model="drawer" title="简报 Markdown" size="50%">
    <pre class="md-preview">{{ preview }}</pre>
  </el-drawer>
</template>

<style scoped>
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.md-preview {
  white-space: pre-wrap;
  font-size: 13px;
  line-height: 1.6;
}
</style>
