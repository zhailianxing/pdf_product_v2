<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUploadRecords } from '@/composables/useUploadRecords'

const router = useRouter()
const { records, fetchRecords, addRecord, loading } = useUploadRecords()

const uploading = ref(false)
const uploadProgress = ref('')
const isDragOver = ref(false)
const fileInput = ref(null)

function resultLabel(value) {
  if (!value) return '—'
  return value
}

function resultClass(value) {
  if (!value) return 'pending'
  return value === 'PASS' ? 'pass' : 'fail'
}

function goReview(record) {
  router.push({
    name: 'Workspace',
    query: { id: record.id, status: record.aiResult.toLowerCase() },
  })
}

function triggerFileInput() {
  if (!uploading.value) {
    fileInput.value?.click()
  }
}

function handleFiles(files) {
  const file = files?.[0]
  if (!file) return
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    alert('请上传 PDF 格式的材质报告文件')
    return
  }
  doUpload(file)
}

async function doUpload(file) {
  uploading.value = true
  uploadProgress.value = '正在上传并调用 AI 识别...'
  try {
    await addRecord(file)
    uploadProgress.value = '上传完成，AI 审核已完成'
    setTimeout(() => {
      uploadProgress.value = ''
    }, 2000)
  } catch (err) {
    alert(err.message || '上传失败')
    uploadProgress.value = ''
  } finally {
    uploading.value = false
  }
}

onMounted(() => {
  fetchRecords()
})

function onFileChange(e) {
  handleFiles(e.target.files)
  e.target.value = ''
}

function onDrop(e) {
  isDragOver.value = false
  handleFiles(e.dataTransfer.files)
}

function onDragOver(e) {
  e.preventDefault()
  isDragOver.value = true
}

function onDragLeave() {
  isDragOver.value = false
}
</script>

<template>
  <div class="upload-records">
    <div class="upload-section card">
      <div class="section-header">
        <h3>上传材质报告</h3>
        <p>支持 PDF 格式，上传后系统将自动调用 Qwen3-VL 进行 AI 识别与审核</p>
      </div>
      <div
        :class="['upload-zone', { 'drag-over': isDragOver, uploading }]"
        @click="triggerFileInput"
        @drop.prevent="onDrop"
        @dragover="onDragOver"
        @dragleave="onDragLeave"
      >
        <input
          ref="fileInput"
          type="file"
          accept=".pdf,application/pdf"
          hidden
          @change="onFileChange"
        />
        <div v-if="uploading" class="upload-loading">
          <span class="spinner dark"></span>
          <span>{{ uploadProgress }}</span>
        </div>
        <template v-else>
          <div class="upload-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
          </div>
          <p class="upload-hint">点击或拖拽 PDF 文件到此处上传</p>
          <p class="upload-sub">单文件上传，文件大小建议不超过 20MB</p>
        </template>
      </div>
      <p v-if="uploadProgress && !uploading" class="upload-success">{{ uploadProgress }}</p>
    </div>

    <div class="records-section card">
      <div class="section-header row">
        <div>
          <h3>上传记录</h3>
          <p>共 {{ records.length }} 条记录</p>
        </div>
      </div>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>报告名称</th>
              <th>厂商</th>
              <th>上传人</th>
              <th>上传时间</th>
              <th>AI 审核结果</th>
              <th>审核员人工审核结果</th>
              <th>管理员抽检结果</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="records.length === 0">
              <td colspan="8" class="empty-cell">暂无上传记录，请先上传 PDF 文件</td>
            </tr>
            <tr v-for="record in records" :key="record.id">
              <td class="name-cell">{{ record.fileName }}</td>
              <td>{{ record.supplier }}</td>
              <td>{{ record.uploader }}</td>
              <td class="time-cell">{{ record.uploadTime }}</td>
              <td>
                <span :class="record.aiResult === 'PASS' ? 'tag tag-pass' : 'tag tag-fail'">
                  {{ record.aiResult }}
                </span>
              </td>
              <td>
                <span :class="['result-text', resultClass(record.manualResult)]">
                  {{ resultLabel(record.manualResult) }}
                </span>
              </td>
              <td>
                <span :class="['result-text', resultClass(record.adminSpotCheckResult)]">
                  {{ resultLabel(record.adminSpotCheckResult) }}
                </span>
              </td>
              <td>
                <button class="btn btn-primary btn-sm" @click="goReview(record)">人工审核</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.upload-records {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-header {
  padding: 16px 20px 0;
}

.section-header.row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 0;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.section-header p {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.upload-zone {
  margin: 16px 20px 20px;
  border: 2px dashed var(--color-border);
  border-radius: 8px;
  padding: 36px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: #f8fafc;
}

.upload-zone:hover:not(.uploading) {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}

.upload-zone.drag-over {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}

.upload-zone.uploading {
  cursor: wait;
  border-color: var(--color-primary);
}

.upload-icon {
  color: var(--color-primary);
  margin-bottom: 12px;
}

.upload-hint {
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 6px;
}

.upload-sub {
  font-size: 12px;
  color: var(--color-text-muted);
}

.upload-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: var(--color-primary);
  font-size: 14px;
}

.spinner.dark {
  border-color: rgba(26, 86, 219, 0.2);
  border-top-color: var(--color-primary);
}

.upload-success {
  padding: 0 20px 16px;
  color: var(--color-pass);
  font-size: 13px;
}

.records-section .section-header {
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border);
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

.result-text {
  font-weight: 600;
  font-size: 13px;
}

.result-text.pending {
  color: var(--color-text-muted);
  font-weight: 400;
}

.result-text.pass {
  color: var(--color-pass);
}

.result-text.fail {
  color: var(--color-fail);
}

.empty-cell {
  text-align: center;
  color: var(--color-text-muted);
  padding: 32px !important;
}
</style>
