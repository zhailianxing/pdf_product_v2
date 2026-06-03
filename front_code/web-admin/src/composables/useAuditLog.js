import { ref } from 'vue'
import { getAuditLogsApi } from '@/api/auditLogs'

export const ACTION_LABELS = {
  UPLOAD: '上传报告',
  AI_AUDIT: 'AI 自动审核',
  MANUAL_CONFIRM_FAIL: '审核员确认不合格',
  MANUAL_OVERRIDE_PASS: '审核员强转合格',
  MANUAL_COMMENT: '添加审核备注',
  ADMIN_SPOT_CHECK: '管理员抽检',
}

const logs = ref([])
const stats = ref({
  total: 0,
  upload: 0,
  aiAudit: 0,
  manual: 0,
  spotCheck: 0,
})
const loading = ref(false)

export function useAuditLog() {
  async function fetchLogs(params = {}) {
    loading.value = true
    try {
      const data = await getAuditLogsApi(params)
      logs.value = data.items
      stats.value = data.stats
    } finally {
      loading.value = false
    }
  }

  function getActionLabel(action) {
    return ACTION_LABELS[action] ?? action
  }

  return { logs, stats, loading, fetchLogs, getActionLabel, ACTION_LABELS }
}
