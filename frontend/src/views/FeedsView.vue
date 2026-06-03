<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { api, unwrap } from "../api/client";
import type { FeedSource, Tag } from "../api/types";

const loading = ref(false);
const saving = ref(false);
const feeds = ref<FeedSource[]>([]);
const tags = ref<Tag[]>([]);
const dialogVisible = ref(false);

const form = reactive({
  name: "",
  feed_url: "",
  tag_id: "",
  is_active: true,
  fetch_interval_minutes: 480,
});

async function loadTags() {
  tags.value = await unwrap<Tag[]>(api.get("/api/v1/tags"));
}

async function load() {
  loading.value = true;
  try {
    const data = await unwrap<{ items: FeedSource[]; total: number }>(
      api.get("/api/v1/feed-sources", { params: { page_size: 100 } })
    );
    feeds.value = data.items;
  } catch (e) {
    ElMessage.error((e as Error).message);
  } finally {
    loading.value = false;
  }
}

function openAddDialog() {
  form.name = "";
  form.feed_url = "";
  form.tag_id = tags.value[0]?.id ?? "";
  form.is_active = true;
  form.fetch_interval_minutes = 480;
  dialogVisible.value = true;
}

async function submitAdd() {
  if (!form.name.trim() || !form.feed_url.trim() || !form.tag_id) {
    ElMessage.warning("请填写名称、RSS 链接并选择板块");
    return;
  }
  saving.value = true;
  try {
    await unwrap(
      api.post("/api/v1/feed-sources", {
        name: form.name.trim(),
        feed_url: form.feed_url.trim(),
        tag_id: form.tag_id,
        is_active: form.is_active,
        fetch_interval_minutes: form.fetch_interval_minutes,
      })
    );
    ElMessage.success("信源已添加");
    dialogVisible.value = false;
    await load();
  } catch (e) {
    ElMessage.error((e as Error).message);
  } finally {
    saving.value = false;
  }
}

async function toggleActive(row: FeedSource, active: boolean) {
  const prev = row.is_active;
  row.is_active = active;
  try {
    await unwrap(
      api.patch(`/api/v1/feed-sources/${row.id}`, { is_active: active })
    );
    ElMessage.success(active ? "已启用" : "已停用");
  } catch (e) {
    row.is_active = prev;
    ElMessage.error((e as Error).message);
  }
}

async function fetchOne(id: string) {
  try {
    const result = await unwrap<{
      articles_created: number;
      articles_skipped: number;
    }>(api.post(`/api/v1/feed-sources/${id}/fetch`));
    ElMessage.success(
      `抓取完成：新增 ${result.articles_created}，跳过 ${result.articles_skipped}`
    );
    await load();
  } catch (e) {
    ElMessage.error((e as Error).message);
  }
}

function tagName(tagId: string) {
  return tags.value.find((t) => t.id === tagId)?.name ?? "—";
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
        <span>RSS 信源</span>
        <el-space>
          <el-button type="primary" size="small" @click="openAddDialog">添加信源</el-button>
          <el-button size="small" @click="load">刷新</el-button>
        </el-space>
      </div>
    </template>
    <el-table v-loading="loading" :data="feeds" stripe>
      <el-table-column label="板块" width="100">
        <template #default="{ row }">{{ tagName(row.tag_id) }}</template>
      </el-table-column>
      <el-table-column prop="name" label="名称" width="160" />
      <el-table-column prop="feed_url" label="RSS 链接" min-width="280" show-overflow-tooltip />
      <el-table-column label="启用" width="90" align="center">
        <template #default="{ row }">
          <el-switch
            :model-value="row.is_active"
            @change="(v: string | number | boolean) => toggleActive(row, Boolean(v))"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button
            size="small"
            type="primary"
            link
            :disabled="!row.is_active"
            @click="fetchOne(row.id)"
          >
            抓取
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="dialogVisible" title="添加 RSS 信源" width="520px" destroy-on-close>
    <el-form label-width="100px">
      <el-form-item label="板块" required>
        <el-select v-model="form.tag_id" placeholder="选择板块" style="width: 100%">
          <el-option v-for="t in tags" :key="t.id" :label="t.name" :value="t.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="显示名称" required>
        <el-input v-model="form.name" placeholder="例如 BBC News" />
      </el-form-item>
      <el-form-item label="RSS 链接" required>
        <el-input
          v-model="form.feed_url"
          placeholder="https://feeds.bbci.co.uk/news/rss.xml"
        />
      </el-form-item>
      <el-form-item label="启用">
        <el-switch v-model="form.is_active" active-text="启用" inactive-text="停用" />
      </el-form-item>
      <el-form-item label="抓取间隔">
        <el-input-number
          v-model="form.fetch_interval_minutes"
          :min="0"
          :step="60"
        />
        <span class="hint">分钟；0 表示跟随全局（默认 480）</span>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submitAdd">保存</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.hint {
  margin-left: 8px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
</style>
