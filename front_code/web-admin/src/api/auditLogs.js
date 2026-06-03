import { request } from './http'

export function getAuditLogsApi(params = {}) {
  const query = new URLSearchParams()
  if (params.action) query.set('action', params.action)
  if (params.keyword) query.set('keyword', params.keyword)
  const qs = query.toString()
  return request(`/audit-logs${qs ? `?${qs}` : ''}`)
}

export function getActionLabelsApi() {
  return request('/audit-logs/action-labels')
}
