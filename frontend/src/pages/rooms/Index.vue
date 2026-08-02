<template>
  <div class="max-w-5xl mx-auto px-4 py-12">
    <div class="text-center mb-10">
      <h1 class="text-3xl font-bold text-gray-900 mb-3">Book a Room</h1>
      <p class="text-gray-600">Select a room for your meeting or event</p>
    </div>

    <div v-if="pending" class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="i in 3" :key="i" class="bg-white rounded-2xl p-6 animate-pulse">
        <div class="w-12 h-12 bg-gray-200 rounded-xl mb-4"></div>
        <div class="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
        <div class="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div class="h-4 bg-gray-200 rounded w-full"></div>
      </div>
    </div>

    <div v-else class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
      <RouterLink
        v-for="room in rooms"
        :key="room.id"
        :to="`/rooms/${room.id}`"
        class="group bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-all duration-200 border border-gray-100"
      >
        <div class="flex items-start gap-4">
          <div class="w-14 h-14 bg-primary-50 rounded-xl flex items-center justify-center text-primary-600 group-hover:bg-primary-100 transition-colors">
            <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-gray-900 mb-1 group-hover:text-primary-600 transition-colors">
              {{ room.name }}
            </h3>
            <p class="text-sm text-gray-500 mb-3 flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {{ room.location }}
            </p>
            <div class="flex items-center gap-2 mb-3">
              <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                {{ room.capacity }} people
              </span>
              <span class="text-xs" :class="getSlotsColor(room.slotsAvailable)">
                {{ room.slotsAvailable }} slots available
              </span>
            </div>
            <div class="flex flex-wrap gap-1">
              <span
                v-for="feature in room.features"
                :key="feature"
                class="inline-flex items-center px-2 py-0.5 rounded text-xs bg-primary-50 text-primary-600"
              >
                {{ feature }}
              </span>
            </div>
          </div>
        </div>
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { format, addDays, startOfDay } from 'date-fns'
import { useBookingStore } from '@/stores/booking'

const bookingStore = useBookingStore()

const rooms = computed(() => bookingStore.rooms.map(room => ({
  ...room,
  slotsAvailable: bookingStore.getAvailableRoomSlotsCount(room.id)
})))

const pending = ref(true)

onMounted(async () => {
  await bookingStore.fetchRooms()
  await bookingStore.fetchSchedules()
  const today = startOfDay(new Date())
  const end = addDays(today, 7)
  await Promise.all(
    bookingStore.rooms.map(r =>
      bookingStore.fetchRoomScheduleSlots(r.id, format(today, 'yyyy-MM-dd'), format(end, 'yyyy-MM-dd'))
    )
  )
  pending.value = false
})

function getSlotsColor(count: number): string {
  if (count === 0) return 'text-red-500'
  if (count <= 3) return 'text-orange-500'
  return 'text-green-600'
}
</script>
