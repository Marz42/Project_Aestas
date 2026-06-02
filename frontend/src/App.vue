<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const menus = [
  { path: "/", label: "控制台" },
  { path: "/feeds", label: "信源" },
  { path: "/articles", label: "文章" },
  { path: "/briefs", label: "简报" },
  { path: "/prompts", label: "Prompt" },
];

const active = computed(() => route.path);
</script>

<template>
  <el-container class="layout">
    <el-aside width="200px" class="aside">
      <div class="brand">Project Aestas</div>
      <el-menu :default-active="active" router>
        <el-menu-item v-for="m in menus" :key="m.path" :index="m.path">
          {{ m.label }}
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span>新闻聚合管理后台</span>
        <el-button text type="primary" @click="router.push('/prompts')">
          管理 Prompt
        </el-button>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout {
  min-height: 100vh;
}
.aside {
  background: #1f2937;
  color: #fff;
}
.brand {
  padding: 20px 16px;
  font-weight: 700;
  font-size: 16px;
}
.aside :deep(.el-menu) {
  border-right: none;
  background: transparent;
}
.aside :deep(.el-menu-item) {
  color: #e5e7eb;
}
.aside :deep(.el-menu-item.is-active) {
  background: #374151;
  color: #fff;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e5e7eb;
  background: #fff;
}
</style>
