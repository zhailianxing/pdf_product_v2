<script setup>
import { ref, onMounted } from 'vue'
import { getUsersApi } from '@/api/users'

const users = ref([])
const loading = ref(true)

function roleLabel(role) {
  return role === 'admin' ? '管理员' : '审核员'
}

function statusLabel(status) {
  return status === 'active' ? '启用' : '停用'
}

function formatTime(value) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

onMounted(async () => {
  try {
    users.value = await getUsersApi()
  } catch (err) {
    alert(err.message || '加载用户列表失败')
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="users-page">
    <div class="page-header card">
      <div>
        <h2>系统用户管理</h2>
        <p>管理系统登录账号与角色权限</p>
      </div>
      <button class="btn btn-primary">+ 新增用户</button>
    </div>

    <div class="users-table card">
      <div v-if="loading" class="loading-hint">加载中...</div>
      <table v-else class="table">
        <thead>
          <tr>
            <th>用户名</th>
            <th>姓名</th>
            <th>角色</th>
            <th>状态</th>
            <th>最后登录</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td class="username">{{ user.username }}</td>
            <td>{{ user.name }}</td>
            <td>
              <span :class="user.role === 'admin' ? 'tag tag-admin' : 'tag tag-auditor'">
                {{ roleLabel(user.role) }}
              </span>
            </td>
            <td>
              <span :class="user.status === 'active' ? 'tag tag-pass' : 'tag tag-fail'">
                {{ statusLabel(user.status) }}
              </span>
            </td>
            <td class="time-cell">{{ formatTime(user.lastLogin) }}</td>
            <td>
              <button class="btn btn-ghost btn-sm">编辑</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.users-page {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
}

.page-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
}

.page-header p {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.users-table {
  overflow: hidden;
}

.loading-hint {
  padding: 32px;
  text-align: center;
  color: var(--color-text-secondary);
}

.username {
  font-weight: 500;
  color: var(--color-primary);
}

.time-cell {
  color: var(--color-text-secondary);
  font-size: 13px;
}
</style>
