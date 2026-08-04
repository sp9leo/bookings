<template>
  <div class="px-4 py-6 max-w-5xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-bold text-gray-900">Reservation Items</h1>
      <button @click="openAdd" class="px-4 py-2 bg-primary-500 text-white text-sm font-semibold rounded-lg hover:bg-primary-600 transition-colors">Add {{ activeTabLabel }}</button>
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

    <div class="flex gap-2 mb-4">
      <button
        v-for="tab in typeTabs"
        :key="tab.value"
        @click="activeType = tab.value"
        class="px-4 py-2 text-sm font-medium rounded-lg transition-colors"
        :class="activeType === tab.value ? 'bg-primary-100 text-primary-700' : 'text-gray-600 hover:bg-gray-100'"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-gray-50 text-left">
            <th class="px-4 py-3 font-semibold text-gray-600">Name</th>
            <th v-if="activeType !== 'Room'" class="px-4 py-3 font-semibold text-gray-600">Subtitle</th>
            <th v-if="activeType !== 'Person'" class="px-4 py-3 font-semibold text-gray-600">Capacity</th>
            <th v-if="activeType !== 'Person'" class="px-4 py-3 font-semibold text-gray-600">Location</th>
            <th v-if="activeType === 'Room'" class="px-4 py-3 font-semibold text-gray-600">Features</th>
            <th v-if="activeType !== 'Room'" class="px-4 py-3 font-semibold text-gray-600">Class</th>
            <th v-if="activeType !== 'Room'" class="px-4 py-3 font-semibold text-gray-600">Group</th>
            <th v-if="activeType === 'Person'" class="px-4 py-3 font-semibold text-gray-600">Assigned User</th>
            <th class="px-4 py-3 font-semibold text-gray-600">Advance Days</th>
            <th class="px-4 py-3 font-semibold text-gray-600">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredItems" :key="item.id" class="border-t border-gray-100 hover:bg-gray-50">
            <td class="px-4 py-3 font-medium text-gray-900">{{ item.name }}</td>
            <td v-if="activeType !== 'Room'" class="px-4 py-3 text-gray-500">{{ item.subtitle }}</td>
            <td v-if="activeType !== 'Person'" class="px-4 py-3 text-gray-500">{{ item.capacity }}</td>
            <td v-if="activeType !== 'Person'" class="px-4 py-3 text-gray-500">{{ item.location }}</td>
            <td v-if="activeType === 'Room'" class="px-4 py-3">
              <div class="flex flex-wrap gap-1">
                <span v-for="f in item.features" :key="f" class="text-xs px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded">{{ f }}</span>
              </div>
            </td>
            <td v-if="activeType !== 'Room'" class="px-4 py-3 text-gray-500">{{ item.class }}</td>
            <td v-if="activeType !== 'Room'" class="px-4 py-3"><span v-if="getGroupName(item.groupId)" class="text-xs px-2 py-0.5 bg-primary-100 text-primary-700 rounded-full">{{ getGroupName(item.groupId) }}</span></td>
            <td v-if="activeType === 'Person'" class="px-4 py-3 text-gray-500">{{ getUserName(item.userId) }}</td>
            <td class="px-4 py-3 text-gray-500">{{ (item.advanceBookingDays ?? 0) > 0 ? item.advanceBookingDays + ' days' : 'Default' }}</td>
            <td class="px-4 py-3">
              <button @click="openEdit(item)" class="text-primary-600 hover:text-primary-800 text-xs font-semibold mr-3">Edit</button>
              <button @click="confirmDelete(item)" class="text-red-500 hover:text-red-700 text-xs font-semibold">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="filteredItems.length === 0" class="text-center py-8 text-sm text-gray-400">
        No {{ activeTabLabel.toLowerCase() }} yet.
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/50" @click="closeModal"></div>
          <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
            <h2 class="text-lg font-bold text-gray-900 mb-4">{{ editingItem ? 'Edit ' + activeTabLabel : 'Add ' + activeTabLabel }}</h2>
            <div class="space-y-4 mb-6">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Name</label>
                <input v-model="form.name" type="text" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
              </div>
              <div v-if="activeType !== 'Room'">
                <label class="block text-xs font-medium text-gray-600 mb-1">Subtitle</label>
                <input v-model="form.subtitle" type="text" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
              </div>
              <div v-if="activeType !== 'Person'" class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">Capacity</label>
                  <input v-model.number="form.capacity" type="number" min="1" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">Location</label>
                  <input v-model="form.location" type="text" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
                </div>
              </div>
              <div v-if="activeType === 'Room'">
                <label class="block text-xs font-medium text-gray-600 mb-1">Features (comma-separated)</label>
                <input v-model="form.featuresStr" type="text" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
              </div>
              <div v-if="activeType !== 'Room'">
                <label class="block text-xs font-medium text-gray-600 mb-1">Class</label>
                <input v-model="form.class" type="text" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
              </div>
              <div v-if="activeType === 'Person'">
                <label class="block text-xs font-medium text-gray-600 mb-1">Assigned User</label>
                <select v-model="form.userId" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
                  <option value="">— None —</option>
                  <option v-for="u in userOptions" :key="u.id" :value="u.id">{{ u.name }}</option>
                </select>
              </div>
              <div v-if="activeType !== 'Room'">
                <label class="block text-xs font-medium text-gray-600 mb-1">Group</label>
                <select v-model="form.groupId" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
                  <option value="">— None —</option>
                  <option v-for="g in bookingStore.groups ?? []" :key="g.id" :value="g.id">{{ g.name }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Advance booking days (0 = use default)</label>
                <input v-model.number="form.advanceDays" type="number" min="0" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
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
            <h2 class="text-lg font-bold text-gray-900 mb-2">Delete {{ activeTabLabel }}</h2>
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useBookingStore } from '@/stores/booking'
import { useAuthStore } from '@/stores/auth'

const bookingStore = useBookingStore()
const authStore = useAuthStore()
const route = useRoute()

type ItemType = 'Person' | 'Room' | 'Asset'

const typeTabs: { label: string; value: ItemType }[] = [
  { label: 'People', value: 'Person' },
  { label: 'Rooms', value: 'Room' },
  { label: 'Assets', value: 'Asset' },
]

const activeType = ref<ItemType>('Person')
const activeTabLabel = computed(() => typeTabs.find((t) => t.value === activeType.value)?.label || 'Item')

const filteredItems = computed(() =>
  bookingStore.items.filter((i) => i.type === activeType.value)
)

const userOptions = computed<{ id: string; name: string }[]>(() =>
  authStore.users.map((u) => ({ id: u.id, name: u.name }))
)

const showModal = ref(false)
const editingItem = ref<{ id: string } | null>(null)
const deleteTarget = ref<{ id: string; name: string } | null>(null)
const deleteWarn = ref('')

const form = reactive({
  name: '',
  subtitle: '',
  class: '',
  userId: '',
  groupId: '',
  capacity: 10,
  location: '',
  featuresStr: '',
  advanceDays: 0,
})

const newGroupName = ref('')

function parseFeatures(s: string): string[] {
  return s.split(',').map((f) => f.trim()).filter(Boolean)
}

function resetForm() {
  form.name = ''
  form.subtitle = ''
  form.class = ''
  form.userId = ''
  form.groupId = ''
  form.capacity = 10
  form.location = ''
  form.featuresStr = ''
  form.advanceDays = 0
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

function openEdit(item: any) {
  editingItem.value = { id: item.id }
  form.name = item.name || ''
  form.subtitle = item.subtitle || ''
  form.class = item.class || ''
  form.userId = item.userId || ''
  form.groupId = item.groupId ?? ''
  form.capacity = item.capacity || 10
  form.location = item.location || ''
  form.featuresStr = (item.features || []).join(', ')
  form.advanceDays = item.advanceBookingDays || 0
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingItem.value = null
}

watch(activeType, () => closeModal())

async function handleSave() {
  if (!form.name) return
  const data: Record<string, any> = { name: form.name, type: activeType.value }
  if (activeType.value !== 'Room') {
    data.subtitle = form.subtitle
    data.class = form.class
    data.groupId = form.groupId || undefined
  }
  if (activeType.value === 'Person') {
    data.userId = form.userId
  }
  if (activeType.value !== 'Person') {
    data.capacity = form.capacity
    data.location = form.location
  }
  if (activeType.value === 'Room') {
    data.features = parseFeatures(form.featuresStr)
  }
  data.advanceBookingDays = form.advanceDays || 0
  if (editingItem.value) {
    await bookingStore.updateItem(editingItem.value.id, data)
  } else {
    await bookingStore.addItem(data)
  }
  closeModal()
}

function getUserName(userId: string): string {
  return userOptions.value.find((u) => u.id === userId)?.name || '—'
}

function getGroupName(groupId?: string): string {
  if (!groupId) return ''
  const groups = (bookingStore.groups ?? []) as Array<{ id: string; name: string }>
  return groups.find((g) => g.id === groupId)?.name || ''
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
  const initialType = route.query.type
  if (initialType === 'Room' || initialType === 'Asset') {
    activeType.value = initialType
  }
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
