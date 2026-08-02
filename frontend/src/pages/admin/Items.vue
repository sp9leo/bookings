<template>
  <div class="px-4 py-6 max-w-5xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-bold text-gray-900">Tutoring Item Management</h1>
      <button @click="openAdd" class="px-4 py-2 bg-primary-500 text-white text-sm font-semibold rounded-lg hover:bg-primary-600 transition-colors">Add Item</button>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 p-6 mb-6">
      <h2 class="text-sm font-semibold text-gray-900 mb-4">Item Groups</h2>
      <div class="flex flex-wrap items-center gap-2 mb-4">
        <span
          v-for="group in bookingStore.groups ?? []"
          :key="group.id"
          class="inline-flex items-center gap-2 px-3 py-1.5 bg-primary-50 text-primary-700 rounded-full text-sm font-medium"
        >
          <input
            :value="group.name"
            @change="(e: any) => bookingStore.updateGroup(group.id, e.target.value)"
            class="bg-transparent outline-none w-32 focus:bg-white focus:ring-2 focus:ring-primary-200 rounded px-1 py-0.5"
          />
          <button @click="removeGroup(group.id)" class="text-primary-400 hover:text-red-500" title="Delete group">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </span>
      </div>
      <div class="flex gap-2">
        <input
          v-model="newGroupName"
          @keyup.enter="addGroup"
          type="text"
          placeholder="New group name"
          class="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
        <button @click="addGroup" :disabled="!newGroupName.trim()" class="px-4 py-2 bg-gray-100 text-gray-700 text-sm font-semibold rounded-lg hover:bg-gray-200 disabled:opacity-50 transition-colors">
          Add Group
        </button>
      </div>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-gray-50 text-left">
            <th class="px-4 py-3 font-semibold text-gray-600">Name</th>
            <th class="px-4 py-3 font-semibold text-gray-600">Subtitle</th>
            <th class="px-4 py-3 font-semibold text-gray-600">Type</th>
            <th class="px-4 py-3 font-semibold text-gray-600">Class</th>
            <th class="px-4 py-3 font-semibold text-gray-600">Group</th>
            <th class="px-4 py-3 font-semibold text-gray-600">Assigned User</th>
            <th class="px-4 py-3 font-semibold text-gray-600">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in bookingStore.items" :key="item.id" class="border-t border-gray-100 hover:bg-gray-50">
            <td class="px-4 py-3 font-medium text-gray-900">{{ item.name }}</td>
            <td class="px-4 py-3 text-gray-500">{{ item.subtitle }}</td>
            <td class="px-4 py-3"><span class="text-xs px-2 py-0.5 bg-blue-100 text-blue-600 rounded-full">{{ item.type }}</span></td>
            <td class="px-4 py-3 text-gray-500">{{ item.class }}</td>
            <td class="px-4 py-3"><span v-if="getGroupName(item.groupId)" class="text-xs px-2 py-0.5 bg-primary-100 text-primary-700 rounded-full">{{ getGroupName(item.groupId) }}</span></td>
            <td class="px-4 py-3 text-gray-500">{{ getUserName(item.userId) }}</td>
            <td class="px-4 py-3">
              <button @click="openEdit(item)" class="text-primary-600 hover:text-primary-800 text-xs font-semibold mr-3">Edit</button>
              <button @click="confirmDelete(item)" class="text-red-500 hover:text-red-700 text-xs font-semibold">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add/Edit Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/50" @click="closeModal"></div>
          <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
            <h2 class="text-lg font-bold text-gray-900 mb-4">{{ editingItem ? 'Edit Item' : 'Add Item' }}</h2>
            <div class="space-y-4 mb-6">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Name</label>
                <input v-model="form.name" type="text" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Subtitle</label>
                <input v-model="form.subtitle" type="text" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">Type</label>
                  <input v-model="form.type" type="text" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">Class</label>
                  <input v-model="form.class" type="text" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
                </div>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Assigned User</label>
                <select v-model="form.userId" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
                  <option value="">— None —</option>
                  <option v-for="u in userOptions" :key="u.id" :value="u.id">{{ u.name }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Group</label>
                <select v-model="form.groupId" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
                  <option value="">— None —</option>
                  <option v-for="g in bookingStore.groups ?? []" :key="g.id" :value="g.id">{{ g.name }}</option>
                </select>
              </div>
            </div>
            <div class="flex gap-3">
              <button @click="closeModal" class="flex-1 py-2.5 bg-gray-100 text-gray-700 font-semibold rounded-xl hover:bg-gray-200 transition-colors text-sm">Cancel</button>
              <button @click="handleSave" :disabled="!form.name" class="flex-1 py-2.5 bg-primary-500 text-white font-semibold rounded-xl hover:bg-primary-600 disabled:bg-gray-300 transition-colors text-sm">Save</button>
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
            <h2 class="text-lg font-bold text-gray-900 mb-2">Delete Item</h2>
            <p v-if="deleteWarn" class="text-sm text-amber-600 mb-2">{{ deleteWarn }}</p>
            <p class="text-sm text-gray-500 mb-6">Are you sure you want to delete <strong>{{ deleteTarget.name }}</strong>?</p>
            <div class="flex gap-3">
              <button @click="deleteTarget = null" class="flex-1 py-2.5 bg-gray-100 text-gray-700 font-semibold rounded-xl hover:bg-gray-200 transition-colors text-sm">Cancel</button>
              <button @click="handleDelete" class="flex-1 py-2.5 bg-red-500 text-white font-semibold rounded-xl hover:bg-red-600 transition-colors text-sm">
                {{ deleteWarn ? 'Delete Anyway' : 'Delete' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useBookingStore } from '@/stores/booking'
import { useAuthStore } from '@/stores/auth'

const bookingStore = useBookingStore()
const authStore = useAuthStore()

const userOptions = computed<{ id: string; name: string }[]>(() =>
  authStore.users.map((u) => ({ id: u.id, name: u.name }))
)

const showModal = ref(false)
const editingItem = ref<{ id: string; slotsAvailable: number } | null>(null)
const deleteTarget = ref<{ id: string; name: string } | null>(null)
const deleteWarn = ref('')

const form = reactive({
  name: '',
  subtitle: '',
  type: 'Person',
  class: '',
  userId: '',
  groupId: '',
})

const newGroupName = ref('')

function resetForm() {
  form.name = ''
  form.subtitle = ''
  form.type = 'Person'
  form.class = ''
  form.userId = ''
  form.groupId = ''
}

function addGroup() {
  const name = newGroupName.value.trim()
  if (!name) return
  bookingStore.addGroup(name)
  newGroupName.value = ''
}

function removeGroup(id: string) {
  bookingStore.removeGroup(id)
}

function openAdd() {
  editingItem.value = null
  resetForm()
  showModal.value = true
}


function openEdit(item: { id: string; name: string; subtitle: string; type: string; class: string; userId: string; groupId?: string }) {
  editingItem.value = { id: item.id, slotsAvailable: 0 }
  form.name = item.name
  form.subtitle = item.subtitle
  form.type = item.type
  form.class = item.class
  form.userId = item.userId
  form.groupId = item.groupId ?? ''
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingItem.value = null
}

async function handleSave() {
  if (!form.name) return
  const data = { name: form.name, subtitle: form.subtitle, type: form.type, class: form.class, userId: form.userId, groupId: form.groupId || undefined, slotsAvailable: editingItem.value?.slotsAvailable || 5 }
  if (editingItem.value) {
    await bookingStore.updateItem(editingItem.value.id, data)
  } else {
    await bookingStore.addItem(data)
  }
  closeModal()
}

function getUserName(userId: string): string {
  return userOptions.value.find(u => u.id === userId)?.name || '—'
}

function getGroupName(groupId?: string): string {
  if (!groupId) return ''
  const groups = (bookingStore.groups ?? []) as Array<{ id: string; name: string }>
  return groups.find(g => g.id === groupId)?.name || ''
}

function confirmDelete(item: { id: string; name: string }) {
  deleteTarget.value = item
  deleteWarn.value = ''
}

async function handleDelete() {
  if (!deleteTarget.value) return
  const result = await bookingStore.removeItem(deleteTarget.value.id, !!deleteWarn.value)
  if (typeof result === 'object' && 'hasBookings' in result) {
    deleteWarn.value = `This item has ${result.hasBookings} active booking(s). Delete anyway?`
    return
  }
  deleteTarget.value = null
  deleteWarn.value = ''
}

onMounted(() => {
  bookingStore.fetchAdminItems()
  bookingStore.fetchGroups()
  authStore.fetchUsers()
})
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-active > div:last-child, .modal-leave-active > div:last-child { transition: transform 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from > div:last-child, .modal-leave-to > div:last-child { transform: scale(0.95); }
</style>
