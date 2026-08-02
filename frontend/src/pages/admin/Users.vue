<template>
  <div class="px-4 py-6 max-w-5xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-bold text-gray-900">User Management</h1>
      <button @click="openAdd" class="px-4 py-2 bg-primary-500 text-white text-sm font-semibold rounded-lg hover:bg-primary-600 transition-colors">Add User</button>
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
                {{ user.role }}
              </span>
            </td>
            <td class="px-4 py-3">
              <button @click="openEdit(user)" class="text-primary-600 hover:text-primary-800 text-xs font-semibold mr-3">Edit</button>
              <button @click="confirmDelete(user)" class="text-red-500 hover:text-red-700 text-xs font-semibold">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="authStore.users.length === 0" class="p-6 text-center text-sm text-gray-400">No users found.</div>
    </div>

    <!-- Add/Edit Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/50" @click="closeModal"></div>
          <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
            <h2 class="text-lg font-bold text-gray-900 mb-4">{{ editingUser ? 'Edit User' : 'Add User' }}</h2>

            <div class="space-y-4 mb-6">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Name</label>
                <input v-model="form.name" type="text" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Email</label>
                <input v-model="form.email" type="email" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
              </div>
              <div v-if="!editingUser">
                <label class="block text-xs font-medium text-gray-600 mb-1">Password</label>
                <input v-model="form.password" type="password" placeholder="Set a login password" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Color</label>
                <div class="flex items-center gap-3">
                  <input v-model="form.color" type="color" class="w-10 h-10 p-0.5 rounded border border-gray-200 cursor-pointer" />
                  <input v-model="form.color" type="text" class="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono" />
                </div>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Role</label>
                <select v-model="form.role" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            </div>

            <div class="flex gap-3">
              <button @click="closeModal" class="flex-1 py-2.5 bg-gray-100 text-gray-700 font-semibold rounded-xl hover:bg-gray-200 transition-colors text-sm">Cancel</button>
              <button @click="handleSave" :disabled="!form.name || !form.email || (!editingUser && !form.password)" class="flex-1 py-2.5 bg-primary-500 text-white font-semibold rounded-xl hover:bg-primary-600 disabled:bg-gray-300 transition-colors text-sm">Save</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Delete Confirm Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="deleteTarget" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/50" @click="deleteTarget = null"></div>
          <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-sm p-6">
            <h2 class="text-lg font-bold text-gray-900 mb-2">Delete User</h2>
            <p class="text-sm text-gray-500 mb-6">Are you sure you want to delete <strong>{{ deleteTarget.name }}</strong>?</p>
            <div class="flex gap-3">
              <button @click="deleteTarget = null" class="flex-1 py-2.5 bg-gray-100 text-gray-700 font-semibold rounded-xl hover:bg-gray-200 transition-colors text-sm">Cancel</button>
              <button @click="handleDelete" class="flex-1 py-2.5 bg-red-500 text-white font-semibold rounded-xl hover:bg-red-600 transition-colors text-sm">Delete</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import type { CurrentUser } from '@/stores/auth'

const authStore = useAuthStore()

const showModal = ref(false)
const editingUser = ref<CurrentUser | null>(null)
const deleteTarget = ref<CurrentUser | null>(null)

const form = reactive({
  name: '',
  email: '',
  password: '',
  color: '#3B82F6',
  role: 'user' as 'admin' | 'user',
})

function resetForm() {
  form.name = ''
  form.email = ''
  form.password = ''
  form.color = '#3B82F6'
  form.role = 'user'
}

function openAdd() {
  editingUser.value = null
  resetForm()
  showModal.value = true
}

function openEdit(user: CurrentUser) {
  editingUser.value = user
  form.name = user.name
  form.email = user.email
  form.password = ''
  form.color = user.color
  form.role = user.role
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingUser.value = null
}

async function handleSave() {
  if (!form.name || !form.email) return
  if (editingUser.value) {
    await authStore.updateUser(editingUser.value.id, { name: form.name, email: form.email, color: form.color, role: form.role })
  } else {
    await authStore.addUser({ name: form.name, email: form.email, color: form.color, role: form.role, password: form.password })
  }
  closeModal()
}

function confirmDelete(user: CurrentUser) {
  deleteTarget.value = user
}

async function handleDelete() {
  if (!deleteTarget.value) return
  await authStore.removeUser(deleteTarget.value.id)
  deleteTarget.value = null
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
