<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDashboardApi } from '@/api/dashboard'

const router = useRouter()

const kpi = ref(null)
const pendingQueue = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const data = await getDashboardApi()
    kpi.value = data.kpi
    pendingQueue.value = data.pendingQueue
  } catch (err) {
    alert(err.message || '加载仪表盘失败')
  } finally {
    loading.value = false
  }
})

const kpiCards = computed(() => {
  if (!kpi.value) return []
  return [
    {
      key: 'total',
      label: '总上传报告数',
      value: kpi.value.totalReports.toLocaleString(),
      unit: '份',
      trend: kpi.value.trends.totalReports,
      trendUp: true,
      icon: 'file',
      color: '#1a56db',
    },
    {
      key: 'pass',
      label: '自动通过率 (PASS)',
      value: kpi.value.passRate,
      unit: '%',
      trend: kpi.value.trends.passRate,
      trendUp: true,
      icon: 'check',
      color: '#059669',
    },
    {
      key: 'fail',
      label: '人工介入率 (FAIL)',
      value: kpi.value.failRate,
      unit: '%',
      trend: kpi.value.trends.failRate,
      trendUp: false,
      icon: 'alert',
      color: '#dc2626',
    },
    {
      key: 'time',
      label: 'AI 识别平均耗时',
      value: kpi.value.avgProcessTime,
      unit: '秒',
      trend: kpi.value.trends.avgProcessTime,
      trendUp: false,
      icon: 'clock',
      color: '#d97706',
    },
  ]
})

function goAudit(item) {
  router.push({ name: 'Workspace', query: { status: 'fail', id: item.id } })
}
</script>

<template>
  <div class="dashboard">
    <div v-if="loading" class="loading-hint">加载中...</div>
    <template v-else>
      <div class="kpi-row">
        <div v-for="card in kpiCards" :key="card.key" class="kpi-card card">
          <div class="kpi-header">
            <div class="kpi-icon" :style="{ background: card.color + '15', color: card.color }">
              <svg v-if="card.icon === 'file'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
              </svg>
              <svg v-else-if="card.icon === 'check'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                <polyline points="22 4 12 14.01 9 11.01" />
              </svg>
              <svg v-else-if="card.icon === 'alert'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                <line x1="12" y1="9" x2="12" y2="13" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
            </div>
            <span :class="['trend', card.trendUp ? 'up' : 'down']">{{ card.trend }}</span>
          </div>
          <div class="kpi-value">
            {{ card.value }}<span class="kpi-unit">{{ card.unit }}</span>
          </div>
          <div class="kpi-label">{{ card.label }}</div>
        </div>
      </div>

      <div class="content-row">
        <div class="queue-panel card">
          <div class="panel-header">
            <h3>待审核队列</h3>
            <span class="tag tag-fail">{{ pendingQueue.length }} 待处理</span>
          </div>
          <div class="table-wrap">
            <table class="table">
              <thead>
                <tr>
                  <th>报告名称</th>
                  <th>厂商</th>
                  <th>报警原因</th>
                  <th>上传时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="pendingQueue.length === 0">
                  <td colspan="5" class="empty-cell">暂无待审核记录</td>
                </tr>
                <tr v-for="item in pendingQueue" :key="item.id">
                  <td class="name-cell">{{ item.fileName }}</td>
                  <td>{{ item.supplier }}</td>
                  <td><span class="reason-tag">{{ item.reason }}</span></td>
                  <td class="time-cell">{{ item.uploadTime }}</td>
                  <td>
                    <button class="btn btn-primary btn-sm" @click="goAudit(item)">去审核</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.loading-hint {
  text-align: center;
  color: var(--color-text-secondary);
  padding: 40px;
}

.kpi-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.kpi-card {
  padding: 16px;
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.kpi-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.trend {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 4px;
}

.trend.up {
  color: var(--color-pass);
  background: var(--color-pass-bg);
}

.trend.down {
  color: var(--color-pass);
  background: var(--color-pass-bg);
}

.kpi-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
}

.kpi-unit {
  font-size: 14px;
  font-weight: 400;
  color: var(--color-text-secondary);
  margin-left: 2px;
}

.kpi-label {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.content-row {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--color-border);
}

.panel-header h3 {
  font-size: 15px;
  font-weight: 600;
}

.table-wrap {
  overflow-x: auto;
}

.name-cell {
  font-weight: 500;
  color: var(--color-primary);
}

.time-cell {
  color: var(--color-text-secondary);
  font-size: 13px;
  white-space: nowrap;
}

.reason-tag {
  display: inline-block;
  padding: 2px 8px;
  background: var(--color-fail-bg);
  color: var(--color-fail);
  border-radius: 4px;
  font-size: 12px;
}

.empty-cell {
  text-align: center;
  color: var(--color-text-muted);
  padding: 24px !important;
}
</style>
