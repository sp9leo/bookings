<template>
  <div class="min-h-screen flex items-center justify-center px-4 bg-gray-50">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <div class="w-14 h-14 bg-primary-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-gray-900">Sign In</h1>
        <p class="text-gray-500 mt-1">Sign in with your account to continue</p>
      </div>

      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              v-model="usr"
              type="text"
              autocomplete="username"
              placeholder="you@school.si"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              v-model="pwd"
              type="password"
              autocomplete="current-password"
              placeholder="Your password"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

          <button
            type="submit"
            :disabled="loading"
            class="w-full px-4 py-2.5 text-sm font-medium bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
          >
            {{ loading ? 'Signing in...' : 'Sign in' }}
          </button>
        </form>
      </div>

      <div class="text-center mt-6">
        <RouterLink
          to="/book"
          class="text-sm text-gray-500 hover:text-primary-600 transition-colors"
        >
          &larr; Back to public booking
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { sessionUser, getSessionUserFromCookie } from '@/data/session'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const usr = ref('')
const pwd = ref('')
const loading = ref(false)
const error = ref('')

onMounted(() => {
  sessionUser.value = getSessionUserFromCookie()
  if (sessionUser.value) {
    router.replace((route.query.redirect as string) || '/rooms')
  }
})

async function handleLogin() {
  if (!usr.value || !pwd.value) {
    error.value = 'Please enter your email and password.'
    return
  }

  loading.value = true
  error.value = ''
  try {
    const ok = await authStore.login(usr.value, pwd.value)
    if (!ok) {
      error.value = 'Invalid email or password.'
      return
    }
    router.push((route.query.redirect as string) || '/rooms')
  } catch {
    error.value = 'Could not connect to server.'
  } finally {
    loading.value = false
  }
}
</script>
