<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { getWorkspaceApi, addCommentApi } from '@/api/records'
import { fetchPdfBlob } from '@/api/http'
import { useUploadRecords } from '@/composables/useUploadRecords'

const route = useRoute()
const { confirmFail, overridePass } = useUploadRecords()

const aiStatus = ref('pass')
const zoom = ref(100)
const rotation = ref(0)
const showCommentModal = ref(false)
const comment = ref('')
const workspace = ref(null)
const pdfBlobUrl = ref('')
const loading = ref(false)

const fileName = computed(() => workspace.value?.record?.fileName ?? '')
const result = computed(
  () =>
    workspace.value?.record?.aiDetail ?? {
      fields: [],
      chemical: [],
      mechanical: [],
      reasons: [],
      chemicalComposition: 'OK',
      mechanicalProperties: 'OK',
    },
)
const failReasons = computed(() => workspace.value?.record?.aiReasons ?? result.value.reasons ?? [])
const isPass = computed(() => aiStatus.value === 'pass')

async function loadWorkspace() {
  const id = route.query.id
  if (!id) return

  loading.value = true
  try {
    const data = await getWorkspaceApi(String(id))
    workspace.value = data
    aiStatus.value = data.aiStatus

    if (pdfBlobUrl.value) {
      URL.revokeObjectURL(pdfBlobUrl.value)
    }
    const blob = await fetchPdfBlob(String(id))
    pdfBlobUrl.value = URL.createObjectURL(blob)
  } catch (err) {
    alert(err.message || '加载工作台失败')
  } finally {
    loading.value = false
  }
}

watch(() => route.query.id, loadWorkspace, { immediate: true })

onUnmounted(() => {
  if (pdfBlobUrl.value) URL.revokeObjectURL(pdfBlobUrl.value)
})

async function handleConfirmFail() {
  if (!route.query.id) return
  try {
    await confirmFail(String(route.query.id), comment.value || undefined)
    await loadWorkspace()
    alert('已确认不合格，记录已保存。')
  } catch (err) {
    alert(err.message || '操作失败')
  }
}

async function handleOverridePass() {
  if (!confirm('确认将此报告强转为合格？此操作将被记录。')) return
  if (!route.query.id) return
  try {
    await overridePass(String(route.query.id), comment.value || undefined)
    aiStatus.value = 'pass'
    await loadWorkspace()
  } catch (err) {
    alert(err.message || '操作失败')
  }
}

function handleAddComment() {
  showCommentModal.value = true
}

async function submitComment() {
  showCommentModal.value = false
  if (!route.query.id) return
  try {
    await addCommentApi(String(route.query.id), comment.value)
    alert(`备注已保存：${comment.value || '（无内容）'}`)
    comment.value = ''
  } catch (err) {
    alert(err.message || '保存备注失败')
  }
}

function zoomIn() {
  zoom.value = Math.min(zoom.value + 10, 200)
}

function zoomOut() {
  zoom.value = Math.max(zoom.value - 10, 50)
}

function rotateDoc() {
  rotation.value = (rotation.value + 90) % 360
}
</script>

<template>
  <div class="workspace">
    <div class="workspace-split">
      <!-- Left: PDF Preview -->
      <div class="preview-panel card">
        <div class="preview-toolbar">
          <div class="toolbar-group">
            <button class="tool-btn" title="放大" @click="zoomIn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
                <line x1="11" y1="8" x2="11" y2="14" /><line x1="8" y1="11" x2="14" y2="11" />
              </svg>
            </button>
            <button class="tool-btn" title="缩小" @click="zoomOut">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
                <line x1="8" y1="11" x2="14" y2="11" />
              </svg>
            </button>
            <button class="tool-btn" title="旋转" @click="rotateDoc">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="23 4 23 10 17 10" />
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
              </svg>
            </button>
          </div>
          <span class="zoom-label">{{ zoom }}%</span>
          <span class="file-name">{{ fileName }}</span>
        </div>
        <div class="preview-body">
          <div v-if="loading" class="loading-hint">加载中...</div>
          <div
            v-else-if="pdfBlobUrl"
            class="pdf-viewer-wrap"
            :style="{ transform: `scale(${zoom / 100}) rotate(${rotation}deg)` }"
          >
            <iframe
              :key="pdfBlobUrl"
              :src="pdfBlobUrl"
              class="pdf-frame"
              title="PDF 原始内容预览"
            />
          </div>
        </div>
      </div>

      <!-- Right: AI Result Panel -->
      <div class="result-panel card">
        <div class="result-scroll">
          <!-- Status Banner -->
          <div :class="['status-banner', isPass ? 'pass' : 'fail']">
            AI Result: {{ isPass ? 'PASS' : 'FAIL' }}
          </div>

          <!-- PASS view -->
          <template v-if="isPass">
            <p class="pass-hint">系统已自动通过，不依赖人工审批，可进入后续业务流程</p>

            <div class="section">
              <h4 class="section-title">提取字段</h4>
              <div class="kv-list">
                <div v-for="field in result.fields" :key="field.label" class="kv-item">
                  <span class="kv-key">{{ field.label }}</span>
                  <span class="kv-value">{{ field.value }}</span>
                </div>
              </div>
            </div>

            <div class="section">
              <h4 class="section-title">审核判定</h4>
              <div class="judgment-row">
                <span>化学成分判定</span>
                <span :class="result.chemicalComposition === 'OK' ? 'tag tag-pass' : 'tag tag-fail'">
                  {{ result.chemicalComposition || 'OK' }}
                </span>
              </div>
              <div class="judgment-row">
                <span>力学性能判定</span>
                <span :class="result.mechanicalProperties === 'OK' ? 'tag tag-pass' : 'tag tag-fail'">
                  {{ result.mechanicalProperties || 'OK' }}
                </span>
              </div>
            </div>

            <div class="section">
              <h4 class="section-title">化学成分</h4>
              <table class="table detail-table">
                <thead>
                  <tr><th>元素</th><th>实测值</th><th>要求</th><th>状态</th></tr>
                </thead>
                <tbody>
                  <tr v-for="row in result.chemical" :key="row.element">
                    <td>{{ row.element }}</td>
                    <td>{{ row.actual }}</td>
                    <td>{{ row.requirement }}</td>
                    <td>
                      <span :class="row.status === 'fail' ? 'tag tag-fail' : 'tag tag-pass'">
                        {{ row.status === 'fail' ? '超标' : 'OK' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="section">
              <h4 class="section-title">力学性能</h4>
              <table class="table detail-table">
                <thead>
                  <tr><th>项目</th><th>实测值</th><th>要求</th><th>状态</th></tr>
                </thead>
                <tbody>
                  <tr v-for="row in result.mechanical" :key="row.property">
                    <td>{{ row.property }}</td>
                    <td>{{ row.actual }}</td>
                    <td>{{ row.requirement }}</td>
                    <td>
                      <span :class="row.status === 'fail' ? 'tag tag-fail' : 'tag tag-pass'">
                        {{ row.status === 'fail' ? '超标' : 'OK' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </template>

          <!-- FAIL view -->
          <template v-else>
            <div class="fail-alert">
              <div class="alert-title">失败原因</div>
              <ul class="reason-list">
                <li v-for="(reason, i) in failReasons" :key="i">❌ {{ reason }}</li>
              </ul>
            </div>

            <div class="section">
              <h4 class="section-title">提取字段</h4>
              <div class="kv-list">
                <div v-for="field in result.fields" :key="field.label" :class="['kv-item', { highlight: field.highlight }]">
                  <span class="kv-key">{{ field.label }}</span>
                  <span :class="['kv-value', { 'text-fail': field.highlight }]">{{ field.value }}</span>
                </div>
              </div>
            </div>

            <div class="section">
              <h4 class="section-title">化学成分（争议指标高亮）</h4>
              <table class="table detail-table">
                <thead>
                  <tr><th>元素</th><th>实测值</th><th>要求</th><th>状态</th></tr>
                </thead>
                <tbody>
                  <tr v-for="row in result.chemical" :key="row.element" :class="{ 'row-fail': row.status === 'fail' }">
                    <td>{{ row.element }}</td>
                    <td>{{ row.actual }}</td>
                    <td>{{ row.requirement }}</td>
                    <td>
                      <span :class="row.status === 'fail' ? 'tag tag-fail' : 'tag tag-pass'">
                        {{ row.status === 'fail' ? '超标' : 'OK' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="section">
              <h4 class="section-title">力学性能</h4>
              <table class="table detail-table">
                <thead>
                  <tr><th>项目</th><th>实测值</th><th>要求</th><th>状态</th></tr>
                </thead>
                <tbody>
                  <tr v-for="row in result.mechanical" :key="row.property">
                    <td>{{ row.property }}</td>
                    <td>{{ row.actual }}</td>
                    <td>{{ row.requirement }}</td>
                    <td><span class="tag tag-pass">OK</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </template>
        </div>

        <!-- FAIL action bar -->
        <div v-if="!isPass" class="action-bar">
          <button class="btn btn-danger" @click="handleConfirmFail">确认不合格 (Confirm Fail)</button>
          <button class="btn btn-warning" @click="handleOverridePass">强转为合格 (Override to Pass)</button>
          <button class="btn btn-ghost" @click="handleAddComment">添加备注 (Add Comment)</button>
        </div>
      </div>
    </div>

    <!-- Comment Modal -->
    <div v-if="showCommentModal" class="modal-overlay" @click.self="showCommentModal = false">
      <div class="modal card">
        <h3>添加审核备注</h3>
        <textarea v-model="comment" rows="4" placeholder="请输入审核备注..."></textarea>
        <div class="modal-actions">
          <button class="btn btn-ghost" @click="showCommentModal = false">取消</button>
          <button class="btn btn-primary" @click="submitComment">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.workspace {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: calc(100vh - var(--topbar-height) - 64px);
}

.workspace-split {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  min-height: 0;
}

.preview-panel,
.result-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.preview-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--color-border);
  background: #f8fafc;
}

.toolbar-group {
  display: flex;
  gap: 4px;
}

.tool-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  background: #fff;
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  transition: all 0.15s;
}

.tool-btn:hover {
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.zoom-label {
  font-size: 12px;
  color: var(--color-text-muted);
  min-width: 40px;
}

.file-name {
  margin-left: auto;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.preview-body {
  flex: 1;
  overflow: auto;
  display: flex;
  align-items: stretch;
  justify-content: center;
  padding: 12px;
  background: #525659;
}

.loading-hint {
  color: #fff;
  align-self: center;
  font-size: 14px;
}

.pdf-viewer-wrap {
  width: 100%;
  height: 100%;
  min-height: 520px;
  transition: transform 0.3s;
  transform-origin: center center;
  background: #fff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}

.pdf-frame {
  width: 100%;
  height: 100%;
  min-height: 520px;
  border: none;
  display: block;
}

.result-panel {
  position: relative;
}

.result-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.status-banner {
  padding: 14px 20px;
  border-radius: 8px;
  font-size: 20px;
  font-weight: 700;
  text-align: center;
  letter-spacing: 1px;
  margin-bottom: 12px;
}

.status-banner.pass {
  background: var(--color-pass-bg);
  color: var(--color-pass);
  border: 2px solid var(--color-pass-border);
}

.status-banner.fail {
  background: var(--color-fail-bg);
  color: var(--color-fail);
  border: 2px solid var(--color-fail-border);
}

.pass-hint {
  color: var(--color-pass);
  font-size: 13px;
  margin-bottom: 16px;
  padding: 8px 12px;
  background: var(--color-pass-bg);
  border-radius: 6px;
}

.fail-alert {
  background: var(--color-fail-bg);
  border: 1px solid var(--color-fail-border);
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
}

.alert-title {
  font-weight: 600;
  color: var(--color-fail);
  margin-bottom: 8px;
}

.reason-list {
  list-style: none;
  font-size: 13px;
  color: #991b1b;
}

.reason-list li {
  padding: 4px 0;
}

.section {
  margin-bottom: 16px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--color-border);
}

.kv-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.kv-item {
  display: flex;
  flex-direction: column;
  padding: 8px 10px;
  background: #f8fafc;
  border-radius: 6px;
  font-size: 13px;
}

.kv-item.highlight {
  background: var(--color-fail-bg);
  border: 1px solid var(--color-fail-border);
}

.kv-key {
  color: var(--color-text-muted);
  font-size: 11px;
  margin-bottom: 2px;
}

.kv-value {
  font-weight: 500;
}

.text-fail {
  color: var(--color-fail);
  font-weight: 700;
}

.judgment-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  font-size: 14px;
}

.detail-table {
  font-size: 13px;
}

.detail-table th,
.detail-table td {
  padding: 6px 10px;
}

.row-fail td {
  background: var(--color-fail-bg);
}

.action-bar {
  display: flex;
  gap: 10px;
  padding: 12px 16px;
  border-top: 1px solid var(--color-border);
  background: #f8fafc;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal {
  width: 420px;
  padding: 24px;
}

.modal h3 {
  margin-bottom: 12px;
}

.modal textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  resize: vertical;
  font-size: 14px;
  margin-bottom: 16px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
