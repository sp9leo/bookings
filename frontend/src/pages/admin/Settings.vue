<template>
  <div class="px-4 py-6 max-w-3xl mx-auto">
    <h1 class="text-xl font-bold text-gray-900 mb-4">Application Settings</h1>

    <div class="space-y-4">
      <div class="bg-white rounded-xl border border-gray-200 p-6">
        <h2 class="text-sm font-semibold text-gray-700 mb-4">Mock Data</h2>
        <p class="text-xs text-gray-400 mb-6">Settings for controlling mock data generation and application behavior will appear here.</p>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="bg-gray-50 rounded-lg p-4">
            <p class="text-xs text-gray-500 mb-1">Total Users</p>
            <p class="text-lg font-bold text-gray-800">{{ authStore.users.length }}</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-4">
            <p class="text-xs text-gray-500 mb-1">Total Rooms</p>
            <p class="text-lg font-bold text-gray-800">{{ bookingStore.rooms.length }}</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-4">
            <p class="text-xs text-gray-500 mb-1">Time Slots</p>
            <p class="text-lg font-bold text-gray-800">{{ bookingStore.timeSlots.length }}</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-4">
            <p class="text-xs text-gray-500 mb-1">Tutoring Items</p>
            <p class="text-lg font-bold text-gray-800">{{ bookingStore.items.length }}</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-4">
            <p class="text-xs text-gray-500 mb-1">Total Bookings</p>
            <p class="text-lg font-bold text-gray-800">{{ totalBookings }}</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-4">
            <p class="text-xs text-gray-500 mb-1">Schedule Slots (all)</p>
            <p class="text-lg font-bold text-gray-800">{{ bookingStore.scheduleSlots.length }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl border border-gray-200 p-6">
        <h2 class="text-sm font-semibold text-gray-700 mb-2">Coming Soon</h2>
        <ul class="text-xs text-gray-400 space-y-1">
          <li>&bull; Regenerate mock data with custom date range</li>
          <li>&bull; Default view preference (Day / Week)</li>
          <li>&bull; Enable / disable sections</li>
          <li>&bull; Data export</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useBookingStore } from '@/stores/booking'

const authStore = useAuthStore()
const bookingStore = useBookingStore()

onMounted(async () => {
  authStore.fetchUsers()
  await bookingStore.fetchGlobalTimeSlots()
})

const totalBookings = computed(() =>
  bookingStore.scheduleSlots.filter(s => (s.bookedCount ?? 0) > 0).length
)
</script>
