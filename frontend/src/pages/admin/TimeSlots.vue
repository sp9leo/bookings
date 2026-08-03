<template>
  <div class="px-4 py-6 max-w-3xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-bold text-gray-900">Room Time Slot Management</h1>
      <div class="flex items-center gap-2">
        <button @click="refresh" :disabled="loading" class="px-4 py-2 bg-gray-100 text-gray-700 text-sm font-semibold rounded-lg hover:bg-gray-200 disabled:opacity-50 transition-colors">
          {{ loading ? 'Refreshing...' : 'Refresh' }}
        </button>
        <button @click="showAddInput = !showAddInput" class="px-4 py-2 bg-primary-500 text-white text-sm font-semibold rounded-lg hover:bg-primary-600 transition-colors">Add Time Slot</button>
      </div>
    </div>

    <div class="bg-blue-50 border border-blue-200 text-blue-800 rounded-xl px-4 py-3 text-sm mb-4">
      Time slots are shared across all rooms and saved to the backend. Changes apply to the day/week views and the room calendar.
      <span v-if="bookingStore.globalScheduleName" class="block mt-1 text-blue-700">Global schedule: <strong>{{ bookingStore.globalScheduleName }}</strong> (edit this record in the backend to add/remove times there)</span>
    </div>

    <div v-if="loadError" class="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm mb-4">{{ loadError }}</div>
    <div v-if="saveError" class="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm mb-4">{{ saveError }}</div>
    <div v-if="saveMessage" class="bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-xl px-4 py-3 text-sm mb-4">{{ saveMessage }}</div>

    <div v-if="showAddInput" class="bg-white rounded-xl border border-gray-200 p-4 mb-4 flex items-center gap-3">
      <input v-model="newTime" type="time" class="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
      <button @click="handleAdd" :disabled="!newTime" class="px-4 py-2 bg-primary-500 text-white text-sm font-semibold rounded-lg hover:bg-primary-600 disabled:bg-gray-300 transition-colors">Add</button>
      <button @click="showAddInput = false; newTime = ''" class="px-4 py-2 bg-gray-100 text-gray-700 text-sm font-semibold rounded-lg hover:bg-gray-200 transition-colors">Cancel</button>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-gray-50 text-left">
            <th class="px-4 py-3 font-semibold text-gray-600 w-12">#</th>
            <th class="px-4 py-3 font-semibold text-gray-600">Time</th>
            <th class="px-4 py-3 font-semibold text-gray-600">Bookings</th>
            <th class="px-4 py-3 font-semibold text-gray-600 w-32">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(ts, i) in bookingStore.timeSlots" :key="ts" class="border-t border-gray-100 hover:bg-gray-50">
            <td class="px-4 py-3 text-gray-400 text-xs">{{ i }}</td>
            <td class="px-4 py-3 font-medium text-gray-900">{{ ts }}</td>
            <td class="px-4 py-3 text-gray-500">{{ slotCounts[i] }}</td>
            <td class="px-4 py-3 flex gap-1">
              <button @click="moveUp(i)" :disabled="i === 0" class="px-2 py-1 text-xs border border-gray-200 rounded hover:bg-gray-100 disabled:opacity-30">&uarr;</button>
              <button @click="moveDown(i)" :disabled="i === bookingStore.timeSlots.length - 1" class="px-2 py-1 text-xs border border-gray-200 rounded hover:bg-gray-100 disabled:opacity-30">&darr;</button>
              <button @click="confirmDelete(i, ts)" class="px-2 py-1 text-xs text-red-500 border border-red-200 rounded hover:bg-red-50">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="bookingStore.timeSlots.length === 0" class="p-6 text-center text-sm text-gray-400">No time slots configured.</div>
    </div>

    <!-- Delete Confirm Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="deleteIndex !== null" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/50" @click="deleteIndex = null"></div>
          <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-sm p-6">
            <h2 class="text-lg font-bold text-gray-900 mb-2">Delete Time Slot</h2>
            <p class="text-sm text-gray-500 mb-2">Remove <strong>{{ deleteTime }}</strong>? This will cancel all bookings at this time.</p>
            <p v-if="deleteSlotCount > 0" class="text-sm text-amber-600 mb-4">{{ deleteSlotCount }} active booking(s) will be cancelled.</p>
            <div class="flex gap-3">
              <button @click="deleteIndex = null" class="flex-1 py-2.5 bg-gray-100 text-gray-700 font-semibold rounded-xl hover:bg-gray-200 transition-colors text-sm">Cancel</button>
              <button @click="handleDeleteTimeSlot" class="flex-1 py-2.5 bg-red-500 text-white font-semibold rounded-xl hover:bg-red-600 transition-colors text-sm">Delete</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useBookingStore } from '@/stores/booking'

const bookingStore = useBookingStore()

const showAddInput = ref(false)
const newTime = ref('')

const deleteIndex = ref<number | null>(null)
const deleteTime = ref('')
const deleteSlotCount = ref(0)

const saveError = ref('')
const saveMessage = ref('')
const loadError = ref('')
const loading = ref(false)

async function refresh() {
  loading.value = true
  loadError.value = ''
  const ok = await bookingStore.fetchGlobalTimeSlots()
  loading.value = false
  if (!ok) loadError.value = 'Could not load time slots from the backend.'
}

function handleVisibility() {
  if (document.visibilityState === 'visible') refresh()
}

onMounted(async () => {
  await refresh()
  window.addEventListener('focus', refresh)
  document.addEventListener('visibilitychange', handleVisibility)
})

onUnmounted(() => {
  window.removeEventListener('focus', refresh)
  document.removeEventListener('visibilitychange', handleVisibility)
})

const slotCounts = computed(() =>
  bookingStore.timeSlots.map(ts =>
    bookingStore.scheduleSlots
      .filter(s => s.time === ts && (s.bookedCount ?? 0) > 0)
      .reduce((sum, s) => sum + (s.bookedCount ?? 0), 0)
  )
)

async function persist() {
  saveError.value = ''
  saveMessage.value = ''
  const ok = await bookingStore.saveGlobalTimeSlots([...bookingStore.timeSlots])
  if (!ok) {
    saveError.value = bookingStore.error || 'Could not save changes. Please try again.'
    return
  }
  saveMessage.value = 'Changes saved.'
  setTimeout(() => {
    if (saveMessage.value === 'Changes saved.') saveMessage.value = ''
  }, 2500)
}

async function handleAdd() {
  if (!newTime.value) return
  if (bookingStore.addTimeSlot(newTime.value)) {
    await persist()
  }
  newTime.value = ''
  showAddInput.value = false
}

async function moveUp(i: number) {
  if (bookingStore.reorderTimeSlot(i, i - 1)) await persist()
}

async function moveDown(i: number) {
  if (bookingStore.reorderTimeSlot(i, i + 1)) await persist()
}

function confirmDelete(i: number, time: string) {
  deleteIndex.value = i
  deleteTime.value = time
  deleteSlotCount.value = bookingStore.scheduleSlots
    .filter(s => s.time === time && (s.bookedCount ?? 0) > 0)
    .reduce((sum, s) => sum + (s.bookedCount ?? 0), 0)
}

async function handleDeleteTimeSlot() {
  if (deleteIndex.value === null) return
  bookingStore.removeTimeSlot(deleteIndex.value)
  deleteIndex.value = null
  await persist()
}
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-active > div:last-child, .modal-leave-active > div:last-child { transition: transform 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from > div:last-child, .modal-leave-to > div:last-child { transform: scale(0.95); }
</style>
