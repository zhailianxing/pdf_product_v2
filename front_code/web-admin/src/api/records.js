import { fetchPdfBlob, request } from './http'

export function getRecordsApi() {
  return request('/records')
}

export function getRecordApi(id) {
  return request(`/records/${id}`)
}

export function getWorkspaceApi(id) {
  return request(`/records/${id}/workspace`)
}

export function uploadRecordApi(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request('/records/upload', {
    method: 'POST',
    body: formData,
  })
}

export function manualReviewApi(id, { action, comment }) {
  return request(`/records/${id}/manual-review`, {
    method: 'POST',
    body: JSON.stringify({ action, comment }),
  })
}

export function addCommentApi(id, comment) {
  return request(`/records/${id}/comment`, {
    method: 'POST',
    body: JSON.stringify({ comment }),
  })
}

export function spotCheckApi(id, { result, comment }) {
  return request(`/records/${id}/spot-check`, {
    method: 'POST',
    body: JSON.stringify({ result, comment }),
  })
}

export { fetchPdfBlob }
