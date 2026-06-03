const API_BASE = import.meta.env.VITE_API_BASE || '/api/v1'

export class ApiError extends Error {
  constructor(message, code = -1) {
    super(message)
    this.code = code
  }
}

function getToken() {
  return localStorage.getItem('mc_token')
}

export async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) }
  const token = getToken()
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }
  if (options.body && !(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json'
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })

  let payload
  try {
    payload = await response.json()
  } catch {
    throw new ApiError(`请求失败 (${response.status})`)
  }

  if (payload.code !== 0) {
    throw new ApiError(payload.message || '请求失败', payload.code)
  }

  return payload.data
}

export async function fetchPdfBlob(recordId) {
  const token = getToken()
  const response = await fetch(`${API_BASE}/records/${recordId}/file`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
  if (!response.ok) {
    throw new ApiError('PDF 加载失败')
  }
  return response.blob()
}

export function saveToken(token) {
  localStorage.setItem('mc_token', token)
}

export function clearToken() {
  localStorage.removeItem('mc_token')
}

export function getStoredToken() {
  return getToken()
}
