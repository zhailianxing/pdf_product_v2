import { request } from './http'

export function loginApi({ username, password, role }) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password, role }),
  })
}

export function getMeApi() {
  return request('/auth/me')
}
