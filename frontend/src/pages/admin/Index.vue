<template>
  <div class="px-4 py-6 max-w-5xl mx-auto">
    <h1 class="text-xl font-bold text-gray-900 mb-4">Admin Dashboard</h1>

    <!-- Admin view -->
    <template v-if="authStore.isAdmin">
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-8">
        <RouterLink to="/admin/users" class="bg-white rounded-xl p-4 border border-gray-200 hover:shadow-md transition-shadow">
          <p class="text-2xl font-bold text-gray-900">{{ authStore.users.length }}</p>
          <p class="text-xs text-gray-500 mt-1">Users</p>
        </RouterLink>
        <RouterLink to="/admin/items?type=Room" class="bg-white rounded-xl p-4 border border-gray-200 hover:shadow-md transition-shadow">
          <p class="text-2xl font-bold text-gray-900">{{ bookingStore.rooms.length }}</p>
          <p class="text-xs text-gray-500 mt-1">Rooms</p>
        </RouterLink>
        <RouterLink to="/admin/time-slots" class="bg-white rounded-xl p-4 border border-gray-200 hover:shadow-md transition-shadow">
          <p class="text-2xl font-bold text-gray-900">{{ bookingStore.timeSlots.length }}</p>
          <p class="text-xs text-gray-500 mt-1">Time Slots</p>
        </RouterLink>
        <RouterLink to="/admin/items" class="bg-white rounded-xl p-4 border border-gray-200 hover:shadow-md transition-shadow">
          <p class="text-2xl font-bold text-gray-900">{{ bookingStore.items.length }}</p>
          <p class="text-xs text-gray-500 mt-1">People</p>
        </RouterLink>
        <RouterLink to="/admin/person-slots" class="bg-white rounded-xl p-4 border border-gray-200 hover:shadow-md transition-shadow">
          <p class="text-2xl font-bold text-gray-900">{{ personSlotCount }}</p>
          <p class="text-xs text-gray-500 mt-1">Person Slots</p>
        </RouterLink>
        <RouterLink to="/admin/bulk-person-slots" class="bg-white rounded-xl p-4 border border-gray-200 hover:shadow-md transition-shadow">
          <p class="text-2xl font-bold text-primary-600">+</p>
          <p class="text-xs text-gray-500 mt-1">Bulk Assign</p>
        </RouterLink>
        <RouterLink to="/admin/bookings" class="bg-white rounded-xl p-4 border border-gray-200 hover:shadow-md transition-shadow">
          <p class="text-2xl font-bold text-gray-900">{{ totalBookings }}</p>
          <p class="text-xs text-gray-500 mt-1">Total Bookings</p>
        </RouterLink>
        <div class="bg-white rounded-xl p-4 border border-gray-200">
          <p class="text-2xl font-bold text-gray-900">{{ upcomingBookings }}</p>
          <p class="text-xs text-gray-500 mt-1">Upcoming</p>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <RouterLink to="/admin/users" class="bg-primary-50 text-primary-700 rounded-xl p-4 border border-primary-200 hover:shadow-md transition-shadow text-sm font-semibold text-center">
          Manage Users &rarr;
        </RouterLink>
        <RouterLink to="/admin/items?type=Room" class="bg-primary-50 text-primary-700 rounded-xl p-4 border border-primary-200 hover:shadow-md transition-shadow text-sm font-semibold text-center">
          Manage Rooms &rarr;
        </RouterLink>
        <RouterLink to="/admin/time-slots" class="bg-primary-50 text-primary-700 rounded-xl p-4 border border-primary-200 hover:shadow-md transition-shadow text-sm font-semibold text-center">
           Room Slots &rarr;
        </RouterLink>
        <RouterLink to="/admin/items" class="bg-primary-50 text-primary-700 rounded-xl p-4 border border-primary-200 hover:shadow-md transition-shadow text-sm font-semibold text-center">
          Manage People &rarr;
        </RouterLink>
        <RouterLink to="/admin/person-slots" class="bg-primary-50 text-primary-700 rounded-xl p-4 border border-primary-200 hover:shadow-md transition-shadow text-sm font-semibold text-center">
          Person Slots &rarr;
        </RouterLink>
        <RouterLink to="/admin/bulk-person-slots" class="bg-primary-50 text-primary-700 rounded-xl p-4 border border-primary-200 hover:shadow-md transition-shadow text-sm font-semibold text-center">
          Bulk Assign Slots &rarr;
        </RouterLink>
        <RouterLink to="/admin/bookings" class="bg-primary-50 text-primary-700 rounded-xl p-4 border border-primary-200 hover:shadow-md transition-shadow text-sm font-semibold text-center">
          All Bookings &rarr;
        </RouterLink>
        <RouterLink to="/admin/settings" class="bg-primary-50 text-primary-700 rounded-xl p-4 border border-primary-200 hover:shadow-md transition-shadow text-sm font-semibold text-center">
          Settings &rarr;
        </RouterLink>
      </div>
    </template>

    <!-- Non-admin view -->
    <template v-else>
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-8">
        <RouterLink to="/my-bookings" class="bg-white rounded-xl p-4 border border-gray-200 hover:shadow-md transition-shadow">
          <p class="text-2xl font-bold text-gray-900">{{ myBookingsCount }}</p>
          <p class="text-xs text-gray-500 mt-1">My Bookings</p>
        </RouterLink>
        <div class="bg-white rounded-xl p-4 border border-gray-200">
          <p class="text-2xl font-bold text-gray-900">{{ myUpcomingCount }}</p>
          <p class="text-xs text-gray-500 mt-1">Upcoming</p>
        </div>
        <div v-if="isTutor" class="bg-white rounded-xl p-4 border border-gray-200">
          <p class="text-2xl font-bold text-gray-900">{{ myItemsCount }}</p>
          <p class="text-xs text-gray-500 mt-1">My Items</p>
        </div>
      </div>

      <div class="bg-white rounded-xl border border-gray-200 p-6 text-center space-y-3">
        <p class="text-gray-500 text-sm">You are logged in as <strong>{{ authStore.currentUser?.name }}</strong></p>
        <div class="flex justify-center gap-4">
          <RouterLink to="/my-bookings" class="text-primary-600 font-semibold text-sm hover:underline">
            View My Bookings &rarr;
          </RouterLink>
          <RouterLink v-if="isTutor" to="/admin/person-slots" class="text-primary-600 font-semibold text-sm hover:underline">
            Manage Your Slots &rarr;
          </RouterLink>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { format, addDays } from 'date-fns'
import { useAuthStore } from '@/stores/auth'
import { useBookingStore } from '@/stores/booking'

const authStore = useAuthStore()
const bookingStore = useBookingStore()

onMounted(async () => {
  authStore.fetchUsers()
  await bookingStore.fetchRooms()
  await bookingStore.fetchItems('Person')
  await bookingStore.fetchGroups()
  await bookingStore.fetchGlobalTimeSlots()

  const start = format(new Date(), 'yyyy-MM-dd')
  const end = format(addDays(new Date(), 90), 'yyyy-MM-dd')
  for (const room of bookingStore.rooms) {
    await bookingStore.fetchRoomScheduleSlots(room.id, start, end)
  }
  for (const item of bookingStore.items) {
    await bookingStore.fetchSlots(item.id)
  }
})

const totalBookings = computed(() =>
  bookingStore.scheduleSlots.filter(s => s.status === 'booked').length
)

const upcomingBookings = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return bookingStore.scheduleSlots.filter(s => {
    if (s.status !== 'booked') return false
    const d = new Date(s.date)
    return d >= today
  }).length
})

const personSlotCount = computed(() =>
  bookingStore.slots.filter(s => s.booked < s.capacity).length
)

const myBookingsCount = computed(() =>
  bookingStore.scheduleSlots.filter(s => s.status === 'booked' && s.bookedBy === authStore.currentUser?.name).length
)

const myUpcomingCount = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return bookingStore.scheduleSlots.filter(s => {
    if (s.status !== 'booked' || s.bookedBy !== authStore.currentUser?.name) return false
    const d = new Date(s.date)
    return d >= today
  }).length
})

const isTutor = computed(() =>
  bookingStore.items.some(item => item.userId === authStore.currentUser?.id)
)

const myItemsCount = computed(() =>
  bookingStore.items.filter(item => item.userId === authStore.currentUser?.id).length
)
</script>
