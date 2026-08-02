<template>
  <div class="px-4 py-6 max-w-5xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-bold text-gray-900">Room Management</h1>
      <button @click="openAdd" class="px-4 py-2 bg-primary-500 text-white text-sm font-semibold rounded-lg hover:bg-primary-600 transition-colors">Add Room</button>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-gray-50 text-left">
            <th class="px-4 py-3 font-semibold text-gray-600">Name</th>
            <th class="px-4 py-3 font-semibold text-gray-600">Capacity</th>
            <th class="px-4 py-3 font-semibold text-gray-600">Location</th>
            <th class="px-4 py-3 font-semibold text-gray-600">Features</th>
            <th class="px-4 py-3 font-semibold text-gray-600">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="room in bookingStore.rooms" :key="room.id" class="border-t border-gray-100 hover:bg-gray-50">
            <td class="px-4 py-3 font-medium text-gray-900">{{ room.name }}</td>
            <td class="px-4 py-3 text-gray-500">{{ room.capacity }}</td>
            <td class="px-4 py-3 text-gray-500">{{ room.location }}</td>
            <td class="px-4 py-3">
              <div class="flex flex-wrap gap-1">
                <span v-for="f in room.features" :key="f" class="text-xs px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded">{{ f }}</span>
              </div>
            </td>
            <td class="px-4 py-3">
              <button @click="openEdit(room)" class="text-primary-600 hover:text-primary-800 text-xs font-semibold mr-3">Edit</button>
              <button @click="confirmDelete(room)" class="text-red-500 hover:text-red-700 text-xs font-semibold">Delete</button>
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
            <h2 class="text-lg font-bold text-gray-900 mb-4">{{ editingRoom ? 'Edit Room' : 'Add Room' }}</h2>
            <div class="space-y-4 mb-6">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Name</label>
                <input v-model="form.name" type="text" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Capacity</label>
                <input v-model.number="form.capacity" type="number" min="1" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Location</label>
                <input v-model="form.location" type="text" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Features (comma-separated)</label>
                <input v-model="form.featuresStr" type="text" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
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
            <h2 class="text-lg font-bold text-gray-900 mb-2">Delete Room</h2>
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
import { ref, reactive, onMounted } from 'vue'
import { useBookingStore } from '@/stores/booking'

interface RoomForm {
  name: string
  capacity: number
  location: string
  featuresStr: string
}

const bookingStore = useBookingStore()

const showModal = ref(false)
const editingRoom = ref<{ id: string } | null>(null)
const deleteTarget = ref<{ id: string; name: string } | null>(null)
const deleteWarn = ref('')

const form = reactive<RoomForm>({
  name: '',
  capacity: 10,
  location: '',
  featuresStr: '',
})

function parseFeatures(s: string): string[] {
  return s.split(',').map(f => f.trim()).filter(Boolean)
}

function resetForm() {
  form.name = ''
  form.capacity = 10
  form.location = ''
  form.featuresStr = ''
}

function openAdd() {
  editingRoom.value = null
  resetForm()
  showModal.value = true
}

function openEdit(room: { id: string; name: string; capacity: number; location: string; features: string[] }) {
  editingRoom.value = { id: room.id }
  form.name = room.name
  form.capacity = room.capacity
  form.location = room.location
  form.featuresStr = room.features.join(', ')
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingRoom.value = null
}

async function handleSave() {
  if (!form.name) return
  const data = { name: form.name, capacity: form.capacity, location: form.location, features: parseFeatures(form.featuresStr) }
  if (editingRoom.value) {
    await bookingStore.updateRoom(editingRoom.value.id, data)
  } else {
    await bookingStore.addRoom(data)
  }
  closeModal()
}

function confirmDelete(room: { id: string; name: string }) {
  deleteTarget.value = room
  deleteWarn.value = ''
}

async function handleDelete() {
  if (!deleteTarget.value) return
  const result = await bookingStore.removeRoom(deleteTarget.value.id, !!deleteWarn.value)
  if (typeof result === 'object' && 'hasBookings' in result) {
    deleteWarn.value = `This room has ${result.hasBookings} active booking(s). Delete anyway?`
    return
  }
  deleteTarget.value = null
  deleteWarn.value = ''
}

onMounted(() => {
  bookingStore.fetchRooms()
})
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-active > div:last-child, .modal-leave-active > div:last-child { transition: transform 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from > div:last-child, .modal-leave-to > div:last-child { transform: scale(0.95); }
</style>
