<script setup>
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { displayName, role, isAdmin, logout } = useAuth()

function handleLogout() {
  logout()
  router.push({ name: 'Login' })
}

const roleLabel = isAdmin.value ? '管理员' : '审核员'
</script>

<template>
  <header class="topbar">
    <div class="topbar-left">
      <div class="logo-icon">
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
          <rect width="28" height="28" rx="6" fill="#1a56db" />
          <path d="M7 18L11 10L14 16L17 8L21 18" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          <circle cx="14" cy="20" r="2" fill="white" opacity="0.8" />
        </svg>
      </div>
      <h1 class="system-title">材质报告 AI 自动审核系统 <span class="version">V1</span></h1>
    </div>
    <div class="topbar-right">
      <div class="user-info">
        <div class="avatar">{{ displayName.charAt(0).toUpperCase() }}</div>
        <div class="user-meta">
          <span class="user-name">{{ displayName }}</span>
          <span :class="['role-tag', isAdmin ? 'tag-admin' : 'tag-auditor']">{{ roleLabel }}</span>
        </div>
      </div>
      <button class="logout-btn" @click="handleLogout" title="退出登录">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
          <polyline points="16 17 21 12 16 7" />
          <line x1="21" y1="12" x2="9" y2="12" />
        </svg>
        退出
      </button>
    </div>
  </header>
</template>

<style scoped>
.topbar {
  height: var(--topbar-height);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.system-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
}

.version {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-primary);
  background: var(--color-primary-light);
  padding: 1px 6px;
  border-radius: 4px;
  margin-left: 4px;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), #3b82f6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.user-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-size: 13px;
  font-weight: 500;
}

.role-tag {
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 3px;
  width: fit-content;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  color: var(--color-text-secondary);
  font-size: 13px;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: var(--color-fail-bg);
  border-color: var(--color-fail-border);
  color: var(--color-fail);
}
</style>
