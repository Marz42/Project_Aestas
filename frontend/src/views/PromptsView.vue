<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { api, unwrap } from "../api/client";
import type { PromptTemplate, Tag } from "../api/types";

const loading = ref(false);
const prompts = ref<PromptTemplate[]>([]);
const tags = ref<Tag[]>([]);
const dialogVisible = ref(false);
const editingId = ref<string | null>(null);

const form = reactive({
  name: "",
  purpose: "extraction",
  description: "",
  system_prompt: "",
  user_prompt_template: "",
});

const placeholders = "{tag_name} {tag_slug} {title} {url} {body}";

const dialogTitle = computed(() => (editingId.value ? "编辑 Prompt" : "新建 Prompt"));

async function load() {
  loading.value = true;
  try {
    const [promptList, tagList] = await Promise.all([
      unwrap<PromptTemplate[]>(api.get("/api/v1/prompt-templates")),
      unwrap<Tag[]>(api.get("/api/v1/tags")),
    ]);
    prompts.value = promptList;
    tags.value = tagList;
  } catch (e) {
    ElMessage.error((e as Error).message);
  } finally {
    loading.value = false;
  }
}

function resetForm() {
  editingId.value = null;
  form.name = "";
  form.purpose = "extraction";
  form.description = "";
  form.system_prompt =
    "你是专业新闻编辑助手。根据原文提取线索，严禁编造未出现的事实或数据。\n输出必须完全依据原文；source_url 必须与用户提供的链接一致。";
  form.user_prompt_template = `板块: {tag_name} ({tag_slug})
标题: {title}
原文链接: {url}

正文或摘要:
{body}`;
}

function openCreate() {
  resetForm();
  dialogVisible.value = true;
}

function openEdit(row: PromptTemplate) {
  editingId.value = row.id;
  form.name = row.name;
  form.purpose = row.purpose;
  form.description = row.description || "";
  form.system_prompt = row.system_prompt;
  form.user_prompt_template = row.user_prompt_template;
  dialogVisible.value = true;
}

async function save() {
  try {
    const payload = {
      name: form.name,
      purpose: form.purpose,
      description: form.description || null,
      system_prompt: form.system_prompt,
      user_prompt_template: form.user_prompt_template,
    };
    if (editingId.value) {
      await unwrap(api.patch(`/api/v1/prompt-templates/${editingId.value}`, payload));
      ElMessage.success("已更新");
    } else {
      await unwrap(api.post("/api/v1/prompt-templates", payload));
      ElMessage.success("已创建");
    }
    dialogVisible.value = false;
    await load();
  } catch (e) {
    ElMessage.error((e as Error).message);
  }
}

async function remove(row: PromptTemplate) {
  await ElMessageBox.confirm(`删除「${row.name}」？`, "确认");
  try {
    await unwrap(api.delete(`/api/v1/prompt-templates/${row.id}`));
    ElMessage.success("已删除");
    await load();
  } catch (e) {
    ElMessage.error((e as Error).message);
  }
}

function tagName(tagId: string | null) {
  if (!tagId) return "—";
  return tags.value.find((t) => t.id === tagId)?.name || tagId.slice(0, 8);
}

async function assignTag(tag: Tag, promptId: string | null) {
  try {
    await unwrap(
      api.patch(`/api/v1/tags/${tag.id}`, {
        prompt_template_id: promptId || null,
      })
    );
    ElMessage.success(`已为「${tag.name}」设置 Prompt`);
    await load();
  } catch (e) {
    ElMessage.error((e as Error).message);
  }
}

onMounted(load);
</script>

<template>
  <el-row :gutter="16">
    <el-col :span="14">
      <el-card>
        <template #header>
          <div class="row">
            <span>已保存的 Prompt</span>
            <el-button type="primary" size="small" @click="openCreate">新建</el-button>
          </div>
        </template>
        <el-table v-loading="loading" :data="prompts" stripe>
          <el-table-column prop="name" label="名称" min-width="140" />
          <el-table-column prop="purpose" label="用途" width="100" />
          <el-table-column label="操作" width="160">
            <template #default="{ row }">
              <el-button size="small" link type="primary" @click="openEdit(row)">编辑</el-button>
              <el-button size="small" link type="danger" @click="remove(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <p class="hint">用户模板可用占位符：{{ placeholders }}</p>
      </el-card>
    </el-col>

    <el-col :span="10">
      <el-card header="板块绑定 Prompt">
        <el-table :data="tags" size="small">
          <el-table-column prop="name" label="板块" width="80" />
          <el-table-column label="当前 Prompt">
            <template #default="{ row }">
              {{ tagName(row.prompt_template_id) }}
            </template>
          </el-table-column>
          <el-table-column label="选择" min-width="160">
            <template #default="{ row }">
              <el-select
                :model-value="row.prompt_template_id || ''"
                placeholder="选择 Prompt"
                clearable
                size="small"
                @change="(v: string) => assignTag(row, v || null)"
              >
                <el-option
                  v-for="p in prompts"
                  :key="p.id"
                  :label="p.name"
                  :value="p.id"
                />
              </el-select>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-col>
  </el-row>

  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="720px" destroy-on-close>
    <el-form label-width="100px">
      <el-form-item label="名称" required>
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="用途">
        <el-select v-model="form.purpose" style="width: 100%">
          <el-option label="单条提炼 (extraction)" value="extraction" />
        </el-select>
      </el-form-item>
      <el-form-item label="说明">
        <el-input v-model="form.description" />
      </el-form-item>
      <el-form-item label="System" required>
        <el-input v-model="form.system_prompt" type="textarea" :rows="5" />
      </el-form-item>
      <el-form-item label="User 模板" required>
        <el-input v-model="form.user_prompt_template" type="textarea" :rows="8" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="save">保存</el-button>
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
  margin-top: 12px;
  font-size: 12px;
  color: #6b7280;
}
</style>
