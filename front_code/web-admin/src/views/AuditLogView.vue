<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuditLog } from '@/composables/useAuditLog'

const router = useRouter()
const { logs, stats, fetchLogs, getActionLabel, ACTION_LABELS } = useAuditLog()

const filterAction = ref('')
const filterKeyword = ref('')

const actionOptions = Object.entries(ACTION_LABELS).map(([value, label]) => ({ value, label }))

function actionTagClass(action) {
  const map = {
    UPLOAD: 'tag-neutral',
    AI_AUDIT: 'tag-ai',
    MANUAL_CONFIRM_FAIL: 'tag-fail',
    MANUAL_OVERRIDE_PASS: 'tag-warn',
    MANUAL_COMMENT: 'tag-neutral',
    ADMIN_SPOT_CHECK: 'tag-pass',
  }
  return map[action] ?? 'tag-neutral'
}

function goRecord(recordId) {
  if (recordId) {
    router.push({ name: 'Workspace', query: { id: recordId } })
  }
}

async function loadLogs() {
  await fetchLogs({
    action: filterAction.value || undefined,
    keyword: filterKeyword.value || undefined,
  })
}

onMounted(loadLogs)

watch([filterAction, filterKeyword], () => {
  loadLogs()
})
</script>

<template>
  <div class="audit-log-page">
    <div class="stats-row">
      <div class="stat-card card">
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">日志总数</div>
      </div>
      <div class="stat-card card">
        <div class="stat-value">{{ stats.upload }}</div>
        <div class="stat-label">上传记录</div>
      </div>
      <div class="stat-card card">
        <div class="stat-value">{{ stats.aiAudit }}</div>
        <div class="stat-label">AI 审核</div>
      </div>
      <div class="stat-card card">
        <div class="stat-value">{{ stats.manual }}</div>
        <div class="stat-label">人工操作</div>
      </div>
      <div class="stat-card card">
        <div class="stat-value">{{ stats.spotCheck }}</div>
        <div class="stat-label">管理员抽检</div>
      </div>
    </div>

    <div class="log-panel card">
      <div class="panel-header">
        <div>
          <h3>审核日志</h3>
          <p>记录上传、AI 审核、人工审核、管理员抽检等全流程操作，便于追溯与质量监控</p>
        </div>
        <div class="filters">
          <select v-model="filterAction" class="filter-select">
            <option value="">全部操作类型</option>
            <option v-for="opt in actionOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
          <input
            v-model="filterKeyword"
            type="text"
            class="filter-input"
            placeholder="搜索报告名称 / 操作人 / 详情"
          />
        </div>
      </div>

      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>时间</th>
              <th>操作类型</th>
              <th>报告名称</th>
              <th>操作人</th>
              <th>详情</th>
              <th>结果</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="logs.length === 0">
              <td colspan="6" class="empty-cell">暂无匹配的审核日志</td>
            </tr>
            <tr v-for="log in logs" :key="log.id">
              <td class="time-cell">{{ log.time }}</td>
              <td>
                <span :class="['tag', actionTagClass(log.action)]">
                  {{ getActionLabel(log.action) }}
                </span>
              </td>
              <td>
                <a
                  v-if="log.recordId"
                  href="#"
                  class="file-link"
                  @click.prevent="goRecord(log.recordId)"
                >{{ log.fileName }}</a>
                <span v-else>{{ log.fileName }}</span>
              </td>
              <td>{{ log.operator }}</td>
              <td class="detail-cell">{{ log.detail }}</td>
              <td>
                <span v-if="log.result" :class="log.result === 'PASS' ? 'tag tag-pass' : 'tag tag-fail'">
                  {{ log.result }}
                </span>
                <span v-else class="text-muted">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.audit-log-page {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.stat-card {
  padding: 14px 16px;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-primary);
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.panel-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  flex-wrap: wrap;
}

.panel-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.panel-header p {
  font-size: 13px;
  color: var(--color-text-secondary);
  max-width: 480px;
}

.filters {
  display: flex;
  gap: 8px;
}

.filter-select,
.filter-input {
  padding: 7px 10px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 13px;
}

.filter-input {
  width: 220px;
}

.table-wrap {
  overflow-x: auto;
}

.time-cell {
  white-space: nowrap;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.detail-cell {
  font-size: 13px;
  max-width: 320px;
}

.file-link {
  color: var(--color-primary);
  font-weight: 500;
}

.file-link:hover {
  text-decoration: underline;
}

.text-muted {
  color: var(--color-text-muted);
}

.tag-neutral {
  background: #f1f5f9;
  color: #475569;
}

.tag-ai {
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.tag-warn {
  background: var(--color-warn-bg);
  color: var(--color-warn);
}

.empty-cell {
  text-align: center;
  color: var(--color-text-muted);
  padding: 32px !important;
}
</style>
