<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { api, unwrap } from "../api/client";
import type { StoryCluster, Tag } from "../api/types";

const loading = ref(false);
const clusters = ref<StoryCluster[]>([]);
const tags = ref<Tag[]>([]);
const tagId = ref("");
const page = ref(1);
const pageSize = ref(20);
const total = ref(0);
const drawer = ref(false);
const activeCluster = ref<StoryCluster | null>(null);

async function loadTags() {
  tags.value = await unwrap<Tag[]>(api.get("/api/v1/tags"));
}

async function load() {
  loading.value = true;
  try {
    const params: Record<string, string | number> = {
      page: page.value,
      page_size: pageSize.value,
    };
    if (tagId.value) params.tag_id = tagId.value;
    const data = await unwrap<{ items: StoryCluster[]; total: number }>(
      api.get("/api/v1/story-clusters", { params })
    );
    clusters.value = data.items;
    total.value = data.total;
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

function openCluster(row: StoryCluster) {
  activeCluster.value = row;
  drawer.value = true;
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
        <span>事件聚类</span>
        <el-space>
          <el-select
            v-model="tagId"
            placeholder="板块"
            clearable
            style="width: 140px"
            @change="onFilterChange"
          >
            <el-option v-for="t in tags" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
          <el-button size="small" @click="load">刷新</el-button>
        </el-space>
      </div>
    </template>
    <el-table v-loading="loading" :data="clusters" stripe>
      <el-table-column prop="tag_name" label="板块" width="90" />
      <el-table-column prop="title" label="事件" min-width="200" show-overflow-tooltip />
      <el-table-column prop="article_count" label="报道数" width="80" />
      <el-table-column prop="window_start" label="窗口起" width="170" />
      <el-table-column label="操作" width="80">
        <template #default="{ row }">
          <el-button size="small" link type="primary" @click="openCluster(row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pager">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        :hide-on-single-page="false"
        layout="total, prev, pager, next"
        background
        @current-change="load"
      />
    </div>
  </el-card>

  <el-drawer v-model="drawer" title="事件详情" size="45%">
    <template v-if="activeCluster">
      <h3>{{ activeCluster.title }}</h3>
      <p class="summary">{{ activeCluster.summary }}</p>
      <el-divider />
      <p><strong>报道来源</strong></p>
      <ul>
        <li v-for="a in activeCluster.articles" :key="a.article_id">
          <el-link :href="a.url" target="_blank" type="primary">
            {{ a.source_name || "来源" }} — {{ a.title }}
          </el-link>
          <el-tag size="small" class="role">{{ a.role }}</el-tag>
        </li>
      </ul>
    </template>
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
.summary {
  color: #4b5563;
  line-height: 1.6;
}
.role {
  margin-left: 8px;
}
</style>
