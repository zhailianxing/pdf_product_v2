import { request } from './http'

export function getDashboardApi() {
  return request('/dashboard')
}
