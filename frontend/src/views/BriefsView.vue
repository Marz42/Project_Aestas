<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { marked } from "marked";
import { ElMessage } from "element-plus";
import { api, unwrap } from "../api/client";
import type { TagBrief } from "../api/types";

const loading = ref(false);
const briefs = ref<TagBrief[]>([]);
const preview = ref("");
const drawer = ref(false);
const page = ref(1);
const pageSize = ref(20);
const total = ref(0);

const renderedHtml = computed(() => {
  if (!preview.value) return "";
  return marked.parse(preview.value, { async: false }) as string;
});

async function load() {
  loading.value = true;
  try {
    const data = await unwrap<{
      items: TagBrief[];
      total: number;
      page: number;
      page_size: number;
    }>(api.get("/api/v1/tag-briefs", { params: { page: page.value, page_size: pageSize.value } }));
    briefs.value = data.items;
    total.value = data.total;
    page.value = data.page;
    pageSize.value = data.page_size;
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

function onPageChange(p: number) {
  page.value = p;
  load();
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
      <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="item_count" label="事件数" width="80" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="openBrief(row)">预览</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pager">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :hide-on-single-page="false"
        layout="total, prev, pager, next"
        background
        @current-change="onPageChange"
      />
    </div>
  </el-card>

  <el-drawer v-model="drawer" title="简报预览" size="55%">
    <div class="md-render" v-html="renderedHtml" />
  </el-drawer>
</template>

<style scoped>
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pager {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
.md-render :deep(h1) {
  font-size: 1.35rem;
  margin-bottom: 0.75rem;
}
.md-render :deep(h2) {
  font-size: 1.1rem;
  margin-top: 1rem;
}
.md-render :deep(a) {
  color: var(--el-color-primary);
}
.md-render :deep(blockquote) {
  color: #6b7280;
  border-left: 3px solid #e5e7eb;
  padding-left: 12px;
}
</style>
