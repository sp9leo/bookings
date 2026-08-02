<template>
  <div class="space-y-6">
    <div v-if="filteredBookings.length === 0" class="text-center py-12">
      <svg class="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <h3 class="text-lg font-semibold text-gray-900 mb-2">No Reservations</h3>
      <p class="text-gray-500">You don't have any reservations yet.</p>
    </div>

    <div v-for="(group, label) in groupedBookings" :key="label" v-show="group.length > 0">
      <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
        {{ label }}
      </h3>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div
          v-for="booking in group"
          :key="booking.id"
          class="flex items-center justify-between px-6 py-4 border-b border-gray-100 last:border-b-0 hover:bg-gray-50 transition-colors"
          :class="{ 'opacity-60': booking.status === 'Cancelled' }"
        >
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-xl flex items-center justify-center" :class="getStatusColor(booking)">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <div>
              <h4 class="font-semibold text-gray-900">{{ booking.roomName }}</h4>
              <div class="flex items-center gap-3 text-sm text-gray-500">
                <span class="flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  {{ formatDate(booking.date) }}
                </span>
                <span class="flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {{ booking.from }} - {{ booking.to }}
                </span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <span
              v-if="booking.status === 'Cancelled'"
              class="px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-700"
            >
              Cancelled
            </span>
            <span
              v-else-if="isPast(booking)"
              class="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-600"
            >
              Completed
            </span>
            <span
              v-else
              class="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-700"
            >
              Confirmed
            </span>

            <button
              v-if="canEdit(booking)"
              @click="$emit('edit', booking)"
              class="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
              title="Edit"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>

            <button
              v-if="canEdit(booking)"
              @click="$emit('cancel', booking)"
              class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              title="Cancel"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { format, parseISO } from 'date-fns'

interface RoomBooking {
  id: string
  roomSlotId: string
  roomName: string
  roomId: string
  date: string
  from: string
  to: string
  userName: string
  userEmail: string
  status: 'Confirmed' | 'Cancelled'
  bookingRef: string
}

const props = defineProps<{
  bookings: RoomBooking[]
  filter?: 'all' | 'upcoming' | 'past'
}>()

defineEmits<{
  (e: 'edit', booking: RoomBooking): void
  (e: 'cancel', booking: RoomBooking): void
}>()

const filteredBookings = computed(() => {
  if (props.filter === 'upcoming') {
    const now = new Date()
    return props.bookings.filter(b => {
      const bookingDate = parseISO(`${b.date}T${b.from}`)
      return bookingDate >= now && b.status === 'Confirmed'
    })
  }
  if (props.filter === 'past') {
    const now = new Date()
    return props.bookings.filter(b => {
      const bookingDate = parseISO(`${b.date}T${b.from}`)
      return bookingDate < now
    })
  }
  return props.bookings
})

const groupedBookings = computed(() => {
  const groups: Record<string, RoomBooking[]> = {
    'Today': [],
    'Upcoming': [],
    'Past': [],
  }

  const now = new Date()
  now.setHours(0, 0, 0, 0)

  filteredBookings.value.forEach(booking => {
    const bookingDate = parseISO(booking.date)
    bookingDate.setHours(0, 0, 0, 0)

    if (bookingDate.getTime() === now.getTime()) {
      groups['Today'].push(booking)
    } else if (bookingDate > now) {
      groups['Upcoming'].push(booking)
    } else {
      groups['Past'].push(booking)
    }
  })

  return groups
})

function formatDate(dateStr: string): string {
  try {
    return format(parseISO(dateStr), 'EEE, MMM d')
  } catch {
    return dateStr
  }
}

function isPast(booking: RoomBooking): boolean {
  const bookingDate = parseISO(`${booking.date}T${booking.from}`)
  return bookingDate < new Date()
}

function canEdit(booking: RoomBooking): boolean {
  const bookingDate = parseISO(`${booking.date}T${booking.from}`)
  return bookingDate >= new Date() && booking.status === 'Confirmed'
}

function getStatusColor(booking: RoomBooking) {
  if (booking.status === 'Cancelled') {
    return 'bg-red-100 text-red-600'
  }
  if (isPast(booking)) {
    return 'bg-gray-100 text-gray-600'
  }
  return 'bg-primary-100 text-primary-600'
}
</script>
