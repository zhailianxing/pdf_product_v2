import { ref, computed } from 'vue'
import { loginApi } from '@/api/auth'
import { clearToken, saveToken } from '@/api/http'
import { ApiError } from '@/api/http'

const user = ref(null)

function loadUser() {
  const raw = localStorage.getItem('mc_auth')
  if (raw) {
    try {
      user.value = JSON.parse(raw)
    } catch {
      user.value = null
    }
  }
}

loadUser()

export function useAuth() {
  const isLoggedIn = computed(() => !!user.value && !!localStorage.getItem('mc_token'))
  const role = computed(() => user.value?.role ?? '')
  const username = computed(() => user.value?.username ?? '')
  const displayName = computed(() => user.value?.name ?? user.value?.username ?? '')
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login({ username: name, password, role: userRole }) {
    const data = await loginApi({ username: name, password, role: userRole })
    saveToken(data.token)
    user.value = {
      id: data.user.id,
      username: data.user.username,
      name: data.user.name,
      role: data.user.role,
      status: data.user.status,
    }
    localStorage.setItem('mc_auth', JSON.stringify(user.value))
    return user.value
  }

  function logout() {
    user.value = null
    localStorage.removeItem('mc_auth')
    clearToken()
  }

  return { user, isLoggedIn, role, username, displayName, isAdmin, login, logout }
}
