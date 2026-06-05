import { createRouter, createWebHistory } from "vue-router";
import DashboardView from "../views/DashboardView.vue";
import FeedsView from "../views/FeedsView.vue";
import ArticlesView from "../views/ArticlesView.vue";
import BriefsView from "../views/BriefsView.vue";
import PromptsView from "../views/PromptsView.vue";
import ClustersView from "../views/ClustersView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: DashboardView },
    { path: "/feeds", component: FeedsView },
    { path: "/articles", component: ArticlesView },
    { path: "/clusters", component: ClustersView },
    { path: "/briefs", component: BriefsView },
    { path: "/prompts", component: PromptsView },
  ],
});

export default router;
