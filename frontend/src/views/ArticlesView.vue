<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { api, unwrap } from "../api/client";
import type { Article, Tag } from "../api/types";

const loading = ref(false);
const articles = ref<Article[]>([]);
const tags = ref<Tag[]>([]);
const status = ref<string>("");
const tagId = ref<string>("");
const page = ref(1);
const pageSize = ref(20);
const total = ref(0);

async function loadTags() {
  try {
    tags.value = await unwrap<Tag[]>(api.get("/api/v1/tags"));
  } catch (e) {
    ElMessage.error((e as Error).message);
  }
}

async function load() {
  loading.value = true;
  try {
    const params: Record<string, string | number> = {
      page: page.value,
      page_size: pageSize.value,
    };
    if (status.value) params.status = status.value;
    if (tagId.value) params.tag_id = tagId.value;
    const data = await unwrap<{
      items: Article[];
      total: number;
      page: number;
      page_size: number;
    }>(api.get("/api/v1/articles", { params }));
    articles.value = data.items;
    total.value = data.total;
    page.value = data.page;
    pageSize.value = data.page_size;
  } catch (e) {
    ElMessage.error((e as Error).message);
  } finally {
    loading.value = false;
  }
}

function onFilterChange() {
  page.value = 1;
  load();
}

function onPageChange(p: number) {
  page.value = p;
  load();
}

function onSizeChange(size: number) {
  pageSize.value = size;
  page.value = 1;
  load();
}

onMounted(async () => {
  await loadTags();
  await load();
});
</script>

<template>
  <el-card>
    <template #header>
      <div class="row">
        <span>文章库 <span class="total-hint">（共 {{ total }} 条）</span></span>
        <el-space wrap>
          <el-select
            v-model="tagId"
            placeholder="板块"
            clearable
            style="width: 140px"
            @change="onFilterChange"
          >
            <el-option
              v-for="t in tags"
              :key="t.id"
              :label="t.name"
              :value="t.id"
            />
          </el-select>
          <el-select
            v-model="status"
            placeholder="状态"
            clearable
            style="width: 140px"
            @change="onFilterChange"
          >
            <el-option label="pending" value="pending" />
            <el-option label="extracted" value="extracted" />
            <el-option label="failed" value="failed" />
            <el-option label="skipped" value="skipped" />
          </el-select>
          <el-button size="small" @click="load">刷新</el-button>
        </el-space>
      </div>
    </template>
    <el-table v-loading="loading" :data="articles" stripe>
      <el-table-column prop="title" label="标题" min-width="240" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column prop="fetched_at" label="抓取时间" width="180" />
      <el-table-column label="链接" width="80">
        <template #default="{ row }">
          <el-link :href="row.url" target="_blank" type="primary">原文</el-link>
        </template>
      </el-table-column>
    </el-table>
    <div class="pager">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[20, 50, 100]"
        :hide-on-single-page="false"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @current-change="onPageChange"
        @size-change="onSizeChange"
      />
    </div>
  </el-card>
</template>

<style scoped>
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.total-hint {
  font-size: 13px;
  font-weight: normal;
  color: var(--el-text-color-secondary);
}
.pager {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
  display: flex;
  justify-content: flex-end;
}
</style>
