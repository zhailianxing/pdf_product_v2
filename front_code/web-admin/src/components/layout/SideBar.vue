<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const route = useRoute()
const router = useRouter()
const { isAdmin } = useAuth()

const menuItems = computed(() => [
  {
    key: 'dashboard',
    label: '仪表盘概览',
    icon: 'dashboard',
    path: '/dashboard',
    visible: true,
  },
  {
    key: 'records',
    label: '上传记录',
    icon: 'records',
    path: '/records',
    visible: true,
  },
  {
    key: 'audit-logs',
    label: '审核日志',
    icon: 'logs',
    path: '/audit-logs',
    visible: true,
  },
  // {
  //   key: 'workspace',
  //   label: 'AI 审核工作台',
  //   icon: 'workspace',
  //   path: '/workspace',
  //   visible: true,
  // },
  {
    key: 'users',
    label: '系统用户管理',
    icon: 'users',
    path: '/users',
    visible: isAdmin.value,
    disabled: !isAdmin.value,
  },
])

function isActive(path) {
  if (path === '/records') {
    return route.path === '/records' || route.path === '/workspace'
  }
  return route.path === path
}

function navigate(item) {
  if (!item.disabled) {
    router.push(item.path)
  }
}
</script>

<template>
  <aside class="sidebar">
    <nav class="nav-menu">
      <div
        v-for="item in menuItems"
        :key="item.key"
        :class="['nav-item', { active: isActive(item.path), disabled: item.disabled }]"
        @click="navigate(item)"
      >
        <span class="nav-icon">
          <svg v-if="item.icon === 'dashboard'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7" rx="1" />
            <rect x="14" y="3" width="7" height="7" rx="1" />
            <rect x="3" y="14" width="7" height="7" rx="1" />
            <rect x="14" y="14" width="7" height="7" rx="1" />
          </svg>
          <svg v-else-if="item.icon === 'workspace'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <polyline points="10 9 9 9 8 9" />
          </svg>
          <svg v-else-if="item.icon === 'records'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
          <svg v-else-if="item.icon === 'logs'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <line x1="10" y1="9" x2="8" y2="9" />
          </svg>
          <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
          </svg>
        </span>
        <span class="nav-label">{{ item.label }}</span>
      </div>
    </nav>
    <div class="sidebar-footer">
      <div class="model-badge">
        <span class="dot"></span>
        Qwen3-VL 本地模型在线
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.nav-menu {
  padding: 12px 8px;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  color: var(--color-text-secondary);
  font-size: 14px;
  transition: all 0.15s;
  margin-bottom: 2px;
}

.nav-item:hover:not(.disabled) {
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.nav-item.active {
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: 600;
}

.nav-item.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.nav-icon {
  display: flex;
  align-items: center;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid var(--color-border);
}

.model-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--color-text-muted);
  padding: 8px;
  background: #f8fafc;
  border-radius: 6px;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-pass);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
