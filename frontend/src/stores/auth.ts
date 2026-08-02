import { defineStore } from 'pinia'
import { apiGet, apiPost, getCsrfToken } from '@/composables/api'
import { sessionUser, getSessionUserFromCookie } from '@/data/session'

export interface CurrentUser {
  id: string
  name: string
  email: string
  color: string
  role: 'admin' | 'user'
}

const COLORS = ['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EC4899', '#06B6D4', '#F97316', '#6366F1']

function colorForName(name: string): string {
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = (hash * 31 + name.charCodeAt(i)) >>> 0
  }
  return COLORS[hash % COLORS.length]
}

export const MOCK_USERS: CurrentUser[] = []

function rolesIncludeAdmin(roles: string[] = []): boolean {
  return roles.some((r) => r === 'System Manager' || r === 'Bookings Manager')
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    currentUser: null as CurrentUser | null,
    users: [] as CurrentUser[],
    loading: false as boolean,
  }),

  getters: {
    isAuthenticated: (state) => state.currentUser !== null,
    isAdmin: (state) => state.currentUser?.role === 'admin',
  },

  actions: {
    async init() {
      if (getSessionUserFromCookie()) {
        await this.fetchCurrentUser()
      } else {
        this.currentUser = null
      }
    },

    async fetchCurrentUser() {
      const info = await apiGet<any>('/api/method/bookings.api.get_current_user')
      if (!info || info.user === 'Guest') {
        this.currentUser = null
        return null
      }
      const role: 'admin' | 'user' = rolesIncludeAdmin(info.roles) ? 'admin' : 'user'
      const user: CurrentUser = {
        id: info.user,
        email: info.user,
        name: info.full_name || info.user,
        color: colorForName(info.full_name || info.user),
        role,
      }
      this.currentUser = user
      return user
    },

    async login(usr: string, pwd: string): Promise<boolean> {
      this.loading = true
      try {
        const res = await fetch('/api/method/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ usr, pwd }),
        })
        if (!res.ok) return false
        sessionUser.value = getSessionUserFromCookie()
        await this.fetchCurrentUser()
        return true
      } finally {
        this.loading = false
      }
    },

    async logout() {
      try {
        await fetch('/api/method/logout', {
          method: 'POST',
          headers: { 'X-Frappe-CSRF-Token': getCsrfToken() },
        })
      } catch {
        // ignore
      }
      sessionUser.value = null
      this.currentUser = null
    },

    setCurrentUser(user: CurrentUser) {
      this.currentUser = user
    },

    async fetchUsers(): Promise<void> {
      const data = await apiGet<any[]>('/api/method/bookings.api.get_users')
      this.users = (data || []).map((u) => ({
        id: u.name,
        name: u.full_name || u.name,
        email: u.email || u.name,
        color: colorForName(u.full_name || u.name),
        role: u.is_admin ? 'admin' : 'user',
      }))
    },

    async addUser(user?: Partial<CurrentUser> & { password?: string }): Promise<CurrentUser | null> {
      if (!user?.email) return null
      const res = await apiPost<any>('/api/method/bookings.api.create_user', {
        email: user.email,
        full_name: user.name,
        password: user.password || null,
        role: user.role || 'user',
      })
      if (!res?.success) return null
      await this.fetchUsers()
      return {
        id: user.email,
        name: user.name || user.email,
        email: user.email,
        color: colorForName(user.name || user.email),
        role: user.role || 'user',
      }
    },

    async updateUser(id?: string, updates?: Partial<CurrentUser>): Promise<boolean> {
      if (!id) return false
      const res = await apiPost<any>('/api/method/bookings.api.update_user', {
        name: id,
        full_name: updates?.name ?? null,
        role: updates?.role ?? null,
      })
      if (!res?.success) return false
      await this.fetchUsers()
      return true
    },

    async removeUser(id?: string): Promise<boolean> {
      if (!id) return false
      const res = await apiPost<any>('/api/method/bookings.api.delete_user', { name: id })
      if (!res?.success) return false
      this.users = this.users.filter((u) => u.id !== id)
      return true
    },
  },
})
