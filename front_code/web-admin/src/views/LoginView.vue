<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { login } = useAuth()

const username = ref('admin')
const password = ref('')
const role = ref('admin')
const remember = ref(false)
const showPassword = ref(false)
const loading = ref(false)

async function handleLogin() {
  if (!username.value.trim()) return
  loading.value = true
  try {
    await login({
      username: username.value,
      password: password.value,
      role: role.value,
    })
    router.push({ name: 'Dashboard' })
  } catch (err) {
    alert(err.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-visual">
        <div class="visual-content">
          <div class="visual-logo">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <rect width="48" height="48" rx="12" fill="rgba(255,255,255,0.15)" />
              <path d="M12 32L18 18L24 28L30 14L36 32" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
              <circle cx="24" cy="36" r="3" fill="white" opacity="0.7" />
            </svg>
          </div>
          <h2 class="visual-title">材质报告 AI 自动审核系统</h2>
          <p class="visual-desc">本地 Qwen3-VL 视觉识别 · 智能审核 · 质量闭环</p>
          <div class="visual-features">
            <div class="feature-item">
              <span class="feature-dot pass"></span>
              PASS 自动通过
            </div>
            <div class="feature-item">
              <span class="feature-dot fail"></span>
              FAIL 人工确认
            </div>
            <div class="feature-item">
              <span class="feature-dot warn"></span>
              PASS 抽检监控
            </div>
          </div>
        </div>
        <div class="visual-pattern"></div>
      </div>

      <div class="login-form-area">
        <div class="form-header">
          <h3>欢迎登录</h3>
          <p>请输入账号信息进入系统</p>
        </div>

        <form class="login-form" @submit.prevent="handleLogin">
          <div class="form-group">
            <label>用户名 / 邮箱</label>
            <div class="input-wrapper">
              <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
              <input v-model="username" type="text" placeholder="请输入用户名" />
            </div>
          </div>

          <div class="form-group">
            <label>密码</label>
            <div class="input-wrapper">
              <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                <path d="M7 11V7a5 5 0 0 1 10 0v4" />
              </svg>
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="请输入密码"
              />
              <button type="button" class="toggle-pwd" @click="showPassword = !showPassword">
                <svg v-if="showPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
                <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
                  <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
                  <line x1="1" y1="1" x2="23" y2="23" />
                </svg>
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>登录角色</label>
            <div class="role-group">
              <label :class="['role-option', { selected: role === 'admin' }]">
                <input v-model="role" type="radio" value="admin" />
                <span class="role-radio"></span>
                管理员
              </label>
              <label :class="['role-option', { selected: role === 'auditor' }]">
                <input v-model="role" type="radio" value="auditor" />
                <span class="role-radio"></span>
                审核员
              </label>
            </div>
          </div>

          <div class="form-extras">
            <label class="remember">
              <input v-model="remember" type="checkbox" />
              <span class="checkmark"></span>
              记住密码
            </label>
            <a href="#" class="forgot-link" @click.prevent>忘记密码？</a>
          </div>

          <button type="submit" class="btn btn-primary login-btn" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            {{ loading ? '登录中...' : '登 录' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e8effc 0%, #f0f2f5 50%, #dbeafe 100%);
  padding: 24px;
}

.login-card {
  display: flex;
  width: 900px;
  max-width: 100%;
  min-height: 520px;
  background: var(--color-surface);
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.login-visual {
  flex: 1;
  background: linear-gradient(160deg, #1a56db 0%, #1e40af 50%, #0f172a 100%);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  overflow: hidden;
}

.visual-pattern {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 20% 80%, rgba(255,255,255,0.08) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255,255,255,0.06) 0%, transparent 40%),
    linear-gradient(45deg, transparent 48%, rgba(255,255,255,0.03) 49%, rgba(255,255,255,0.03) 51%, transparent 52%);
  background-size: 100% 100%, 100% 100%, 20px 20px;
}

.visual-content {
  position: relative;
  z-index: 1;
  color: #fff;
  text-align: center;
}

.visual-logo {
  margin-bottom: 20px;
}

.visual-title {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 8px;
}

.visual-desc {
  font-size: 13px;
  opacity: 0.8;
  margin-bottom: 32px;
}

.visual-features {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-start;
  margin: 0 auto;
  width: fit-content;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  opacity: 0.9;
}

.feature-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.feature-dot.pass { background: #34d399; }
.feature-dot.fail { background: #f87171; }
.feature-dot.warn { background: #fbbf24; }

.login-form-area {
  flex: 1;
  padding: 48px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.form-header {
  margin-bottom: 28px;
}

.form-header h3 {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 6px;
}

.form-header p {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 6px;
  color: var(--color-text);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 12px;
  color: var(--color-text-muted);
}

.input-wrapper input {
  width: 100%;
  padding: 10px 12px 10px 40px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.input-wrapper input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(26, 86, 219, 0.1);
}

.toggle-pwd {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  color: var(--color-text-muted);
  padding: 4px;
  display: flex;
}

.toggle-pwd:hover {
  color: var(--color-text-secondary);
}

.role-group {
  display: flex;
  gap: 12px;
}

.role-option {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border: 1.5px solid var(--color-border);
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.role-option input {
  display: none;
}

.role-radio {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-border);
  border-radius: 50%;
  position: relative;
  flex-shrink: 0;
}

.role-option.selected {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.role-option.selected .role-radio {
  border-color: var(--color-primary);
}

.role-option.selected .role-radio::after {
  content: '';
  position: absolute;
  inset: 3px;
  background: var(--color-primary);
  border-radius: 50%;
}

.form-extras {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.remember {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: pointer;
}

.remember input {
  display: none;
}

.checkmark {
  width: 16px;
  height: 16px;
  border: 1.5px solid var(--color-border);
  border-radius: 3px;
  position: relative;
}

.remember input:checked + .checkmark {
  background: var(--color-primary);
  border-color: var(--color-primary);
}

.remember input:checked + .checkmark::after {
  content: '✓';
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 11px;
}

.forgot-link {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.forgot-link:hover {
  color: var(--color-primary);
}

.login-btn {
  width: 100%;
  padding: 12px;
  font-size: 15px;
  margin-top: 4px;
}
</style>
