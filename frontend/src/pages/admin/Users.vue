<template>
  <div class="px-4 py-6 max-w-5xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-bold text-gray-900">User Management</h1>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-gray-50 text-left">
            <th class="px-4 py-3 font-semibold text-gray-600">Name</th>
            <th class="px-4 py-3 font-semibold text-gray-600">Email</th>
            <th class="px-4 py-3 font-semibold text-gray-600">Color</th>
            <th class="px-4 py-3 font-semibold text-gray-600">Role</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in authStore.users" :key="user.id" class="border-t border-gray-100 hover:bg-gray-50">
            <td class="px-4 py-3 font-medium text-gray-900">{{ user.name }}</td>
            <td class="px-4 py-3 text-gray-500">{{ user.email }}</td>
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <div class="w-5 h-5 rounded border" :style="{ backgroundColor: user.color, borderColor: user.color }"></div>
                <span class="text-xs text-gray-500">{{ user.color }}</span>
              </div>
            </td>
            <td class="px-4 py-3">
              <span class="text-xs px-2 py-0.5 rounded-full font-medium bg-purple-100 text-purple-700">
                Bookings Manager
              </span>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="authStore.users.length === 0" class="p-6 text-center text-sm text-gray-400">No Bookings Manager users found.</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  authStore.fetchUsers()
})
</script>
