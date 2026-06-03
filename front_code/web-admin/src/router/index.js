import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: { title: '仪表盘概览', breadcrumb: ['首页', '仪表盘概览'] },
      },
      {
        path: 'workspace',
        name: 'Workspace',
        component: () => import('@/views/WorkspaceView.vue'),
        meta: { title: 'AI 审核工作台', breadcrumb: ['首页', '上传记录', 'AI 审核工作台'] },
      },
      {
        path: 'records',
        name: 'UploadRecords',
        component: () => import('@/views/UploadRecordsView.vue'),
        meta: { title: '上传记录', breadcrumb: ['首页', '上传记录'] },
      },
      {
        path: 'audit-logs',
        name: 'AuditLogs',
        component: () => import('@/views/AuditLogView.vue'),
        meta: { title: '审核日志', breadcrumb: ['首页', '审核日志'] },
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/UserManagementView.vue'),
        meta: { title: '系统用户管理', breadcrumb: ['首页', '系统用户管理'], adminOnly: true },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const { isLoggedIn, isAdmin } = useAuth()

  if (!to.meta.public && !isLoggedIn.value) {
    return { name: 'Login' }
  }

  if (to.name === 'Login' && isLoggedIn.value) {
    return { name: 'Dashboard' }
  }

  if (to.meta.adminOnly && !isAdmin.value) {
    return { name: 'Dashboard' }
  }

  return true
})

export default router
