<template>
  <div class="px-4 py-6 max-w-3xl mx-auto">
    <h1 class="text-xl font-bold text-gray-900 mb-4">Application Settings</h1>

    <div class="space-y-4">
      <div class="bg-white rounded-xl border border-gray-200 p-6">
        <h2 class="text-sm font-semibold text-gray-700 mb-4">Booking Window</h2>
        <p class="text-xs text-gray-400 mb-4">How far in advance items can be booked by default. Items with their own override (Advance Booking Days) use that value instead.</p>
        <div class="flex items-end gap-3">
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1" for="advance-days">Default advance booking days</label>
            <input
              id="advance-days"
              v-model.number="advanceDaysInput"
              type="number"
              min="1"
              class="w-40 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <button
            @click="saveAdvanceDays"
            :disabled="saving"
            class="px-4 py-2 bg-primary-500 text-white text-sm font-semibold rounded-lg hover:bg-primary-600 disabled:opacity-50 transition-colors"
          >
            {{ saving ? 'Saving...' : 'Save' }}
          </button>
          <span v-if="saved" class="text-xs text-green-600 font-medium">Saved</span>
        </div>
      </div>

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
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useBookingStore } from '@/stores/booking'

const authStore = useAuthStore()
const bookingStore = useBookingStore()

const advanceDaysInput = ref(30)
const saving = ref(false)
const saved = ref(false)

onMounted(async () => {
  authStore.fetchUsers()
  await bookingStore.fetchGlobalTimeSlots()
  advanceDaysInput.value = bookingStore.bookingSettings.defaultAdvanceBookingDays
})

async function saveAdvanceDays() {
  saving.value = true
  saved.value = false
  const ok = await bookingStore.saveBookingSettings(advanceDaysInput.value || 30)
  saving.value = false
  if (ok) {
    saved.value = true
    setTimeout(() => (saved.value = false), 2000)
  }
}

const totalBookings = computed(() =>
  bookingStore.scheduleSlots.filter(s => (s.bookedCount ?? 0) > 0).length
)
</script>
