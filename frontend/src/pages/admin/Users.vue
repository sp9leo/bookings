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
            <th class="px-4 py-3 font-semibold text-gray-600">Actions</th>
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
              <span class="text-xs px-2 py-0.5 rounded-full font-medium" :class="user.role === 'admin' ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-600'">
                {{ user.role === 'admin' ? 'Bookings Manager' : 'Bookings User' }}
              </span>
            </td>
            <td class="px-4 py-3">
              <button @click="openEdit(user)" class="text-primary-600 hover:text-primary-800 text-xs font-semibold">Edit</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="authStore.users.length === 0" class="p-6 text-center text-sm text-gray-400">No users found.</div>
    </div>

    <!-- Edit Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="editingUser" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/50" @click="closeModal"></div>
          <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
            <h2 class="text-lg font-bold text-gray-900 mb-4">Edit User Color</h2>

            <div class="space-y-4 mb-6">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Name</label>
                <input :value="editingUser.name" type="text" disabled class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg bg-gray-50 text-gray-500" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Email</label>
                <input :value="editingUser.email" type="email" disabled class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg bg-gray-50 text-gray-500" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Role</label>
                <input :value="editingUser.role === 'admin' ? 'Bookings Manager' : 'Bookings User'" type="text" disabled class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg bg-gray-50 text-gray-500" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Color</label>
                <div class="flex items-center gap-3">
                  <input v-model="form.color" type="color" class="w-10 h-10 p-0.5 rounded border border-gray-200 cursor-pointer" />
                  <input v-model="form.color" type="text" class="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono" />
                </div>
              </div>
            </div>

            <div class="flex gap-3">
              <button @click="closeModal" class="flex-1 py-2.5 bg-gray-100 text-gray-700 font-semibold rounded-xl hover:bg-gray-200 transition-colors text-sm">Cancel</button>
              <button @click="handleSave" :disabled="!validColor" class="flex-1 py-2.5 bg-primary-500 text-white font-semibold rounded-xl hover:bg-primary-600 disabled:bg-gray-300 transition-colors text-sm">Save</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import type { CurrentUser } from '@/stores/auth'

const authStore = useAuthStore()

const editingUser = ref<CurrentUser | null>(null)

const form = reactive({
  color: '#3B82F6',
})

const validColor = computed(() => /^#[0-9a-fA-F]{6}$/.test(form.color))

function openEdit(user: CurrentUser) {
  editingUser.value = user
  form.color = user.color
}

function closeModal() {
  editingUser.value = null
}

async function handleSave() {
  if (!editingUser.value || !validColor.value) return
  const ok = await authStore.updateUserColor(editingUser.value.id, form.color)
  if (ok) closeModal()
}

onMounted(() => {
  authStore.fetchUsers()
})
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-active > div:last-child, .modal-leave-active > div:last-child { transition: transform 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from > div:last-child, .modal-leave-to > div:last-child { transform: scale(0.95); }
</style>
