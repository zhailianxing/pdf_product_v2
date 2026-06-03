import { ref } from 'vue'
import {
  getRecordsApi,
  getRecordApi,
  uploadRecordApi,
  manualReviewApi,
} from '@/api/records'

const records = ref([])
const loading = ref(false)

export function useUploadRecords() {
  async function fetchRecords() {
    loading.value = true
    try {
      records.value = await getRecordsApi()
    } finally {
      loading.value = false
    }
  }

  async function getRecord(id) {
    const cached = records.value.find((r) => r.id === id)
    if (cached) return cached
    return getRecordApi(id)
  }

  async function addRecord(file) {
    const record = await uploadRecordApi(file)
    records.value.unshift(record)
    return record
  }

  async function confirmFail(id, comment) {
    const record = await manualReviewApi(id, { action: 'confirm_fail', comment })
    updateLocalRecord(record)
    return record
  }

  async function overridePass(id, comment) {
    const record = await manualReviewApi(id, { action: 'override_pass', comment })
    updateLocalRecord(record)
    return record
  }

  function updateLocalRecord(record) {
    const index = records.value.findIndex((r) => r.id === record.id)
    if (index >= 0) {
      records.value[index] = record
    }
  }

  return {
    records,
    loading,
    fetchRecords,
    getRecord,
    addRecord,
    confirmFail,
    overridePass,
    updateLocalRecord,
  }
}
