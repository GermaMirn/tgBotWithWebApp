import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import Home from "@/views/Home.vue";
import Calendar from "@/views/Calendar.vue";
import WebAccess from "@/views/WebAccess.vue";
import Teachers from "@/views/Teachers.vue";
import Profile from "@/views/Profile.vue";
import RoleSwitch from "@/views/RoleSwitch.vue";
import AdminRoleSwitch from "@/views/AdminRoleSwitch.vue";
import Groups from "@/views/Groups.vue"
import GroupDetailPage from "@/views/GroupDetailPage.vue";
import GroupInvitePage from "@/views/GroupInvitePage.vue";
import AppLayout from "@/layouts/appLayout.vue";

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    redirect: "/home",
  },
  {
    path: "/home",
    name: "Home",
    component: Home,
    meta: { layout: AppLayout },
  },
  {
    path: "/calendar",
    name: "Calendar",
    component: Calendar,
    meta: { layout: AppLayout },
  },
  {
    path: "/teachers",
    name: "Teachers",
    component: Teachers,
    meta: { layout: AppLayout },
  },
  {
    path: "/profile",
    name: "Profile",
    component: Profile,
    meta: { layout: AppLayout },
  },
  {
    path: "/role-switch/:token",
    name: "RoleSwitch",
    component: RoleSwitch,
  },
  {
    path: "/admin/role-switch",
    name: "AdminRoleSwitch",
    component: AdminRoleSwitch,
    meta: { layout: AppLayout, requiresAdmin: true },
  },
  {
    path: "/groups",
    name: "Groups",
    component: Groups,
    meta: { layout: AppLayout },
  },
  {
    path: '/groups/:id',
    name: 'GroupDetail',
    component: GroupDetailPage,
    props: true,
    meta: { layout: AppLayout },
  },
  {
    path: '/groups/invite/:token',
    name: 'GroupInvitePage',
    component: GroupInvitePage,
    props: true,
    meta: { layout: AppLayout },
  },
  {
    path: "/web",
    name: "Web-access",
    component: WebAccess,
    meta: { layout: AppLayout },
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Редирект неизвестных путей на главную (кроме /api*)
router.beforeEach((to, from, next) => {
    if (to.path.startsWith('/api')) {
        window.location.href = to.fullPath;
        return;
    }
    next();
});

export default router;
