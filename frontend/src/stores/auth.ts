import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { UserInfo, LoginData } from '@/api/auth'
import { login as loginApi, getMe } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(JSON.parse(localStorage.getItem('user') || 'null'))
  const token = ref<string | null>(localStorage.getItem('token'))

  async function login(data: LoginData) {
    const res = await loginApi(data)
    token.value = res.data.access
    user.value = res.data.user
    localStorage.setItem('token', res.data.access)
    localStorage.setItem('refresh', res.data.refresh)
    localStorage.setItem('user', JSON.stringify(res.data.user))
  }

  async function fetchUser() {
    try {
      const res = await getMe()
      user.value = res.data
      localStorage.setItem('user', JSON.stringify(res.data))
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refresh')
    localStorage.removeItem('user')
  }

  function hasRole(roles: string[]): boolean {
    return !user.value || roles.includes(user.value.role)
  }

  return { user, token, login, fetchUser, logout, hasRole }
})