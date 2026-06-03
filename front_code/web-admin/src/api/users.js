import { request } from './http'

export function getUsersApi() {
  return request('/users')
}
