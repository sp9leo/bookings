<template>
  <div class="px-4 py-6 max-w-5xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-bold text-gray-900">{{ authStore.isAdmin ? 'All Bookings' : 'My Bookings' }}</h1>
    </div>

    <div v-if="authStore.isAdmin" class="flex flex-wrap gap-3 mb-4">
      <select v-model="filterRoom" class="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
        <option value="">All Rooms</option>
        <option v-for="r in bookingStore.rooms" :key="r.id" :value="r.id">{{ r.name }}</option>
      </select>
      <input v-model="filterUser" type="text" placeholder="Filter by user..." class="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 w-48" />
    </div>

    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-gray-50 text-left">
            <th class="px-4 py-3 font-semibold text-gray-600">Room</th>
            <th class="px-4 py-3 font-semibold text-gray-600">Date</th>
            <th class="px-4 py-3 font-semibold text-gray-600">Time</th>
            <th class="px-4 py-3 font-semibold text-gray-600">User</th>
            <th class="px-4 py-3 font-semibold text-gray-600">Description</th>
            <th class="px-4 py-3 font-semibold text-gray-600">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="slot in filteredSlots" :key="slot.id" class="border-t border-gray-100 hover:bg-gray-50">
            <td class="px-4 py-3 font-medium text-gray-900">{{ getRoomName(slot.roomId) }}</td>
            <td class="px-4 py-3 text-gray-500">{{ slot.date }}</td>
            <td class="px-4 py-3 text-gray-500">{{ slot.time }}</td>
            <td class="px-4 py-3">
              <span class="flex items-center gap-1.5">
                <span class="w-2.5 h-2.5 rounded-full" :style="{ backgroundColor: getUserColor(slot.bookedBy || '') }"></span>
                {{ slot.bookedBy }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-500 max-w-40 truncate">{{ slot.description || '—' }}</td>
            <td class="px-4 py-3">
              <button @click="handleCancel(slot)" class="text-xs font-semibold text-red-500 hover:text-red-700">Cancel</button>
            </td>
          </tr>
          <tr v-if="filteredSlots.length === 0">
            <td colspan="6" class="px-4 py-8 text-center text-sm text-gray-400">No bookings found.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { format, addDays } from 'date-fns'
import { useAuthStore } from '@/stores/auth'
import { useBookingStore } from '@/stores/booking'

const authStore = useAuthStore()
const bookingStore = useBookingStore()

const filterRoom = ref('')
const filterUser = ref('')

const allSlots = computed(() =>
  bookingStore.scheduleSlots.filter(s => (s.bookedCount ?? 0) > 0)
)

const filteredSlots = computed(() => {
  let slots = allSlots.value

  if (!authStore.isAdmin) {
    slots = slots.filter(s => s.bookedBy === authStore.currentUser?.name)
  } else {
    if (filterRoom.value) slots = slots.filter(s => s.roomId === filterRoom.value)
    if (filterUser.value) slots = slots.filter(s =>
      s.bookedBy?.toLowerCase().includes(filterUser.value.toLowerCase())
    )
  }

  return slots.sort((a, b) => a.date.localeCompare(b.date) || a.time.localeCompare(b.time))
})

function getRoomName(roomId: string): string {
  return bookingStore.rooms.find(r => r.id === roomId)?.name || roomId
}

function getUserColor(name: string): string {
  return authStore.users.find(u => u.name === name)?.color || '#6B7280'
}

async function handleCancel(slot: { bookingRef?: string }) {
  if (!slot.bookingRef) return
  if (confirm('Cancel this booking?')) {
    await bookingStore.adminCancelBooking(slot.bookingRef)
  }
}

onMounted(async () => {
  authStore.fetchUsers()
  await bookingStore.fetchRooms()
  const start = format(new Date(), 'yyyy-MM-dd')
  const end = format(addDays(new Date(), 90), 'yyyy-MM-dd')
  for (const room of bookingStore.rooms) {
    await bookingStore.fetchRoomAvailableSlots(room.id, start, end)
  }
})
</script>
