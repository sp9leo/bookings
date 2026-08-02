<template>
  <div class="max-w-2xl mx-auto px-4 py-16 text-center">
    <div class="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
      <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      </div>

      <h1 class="text-2xl font-bold text-gray-900 mb-2">Room Booked!</h1>
      <p class="text-gray-600 mb-8">Your room reservation has been confirmed.</p>

      <div class="bg-gray-50 rounded-xl p-6 text-left mb-8">
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-gray-500">Room</span>
            <span class="font-medium text-gray-900">{{ route.query.room }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">Date</span>
            <span class="font-medium text-gray-900">{{ formatDate(route.query.date as string) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">Time</span>
            <span class="font-medium text-gray-900">{{ route.query.time }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">Booked by</span>
            <span class="font-medium text-gray-900">{{ route.query.name }}</span>
          </div>
        </div>
      </div>

      <div class="bg-primary-500 rounded-xl p-4 mb-8 text-white">
        <p class="text-sm font-medium">
          Booking Reference: <span class="text-xl font-bold tracking-wider">{{ route.query.ref }}</span>
        </p>
        <p class="text-xs text-primary-100 mt-2">
          Save this reference to view or cancel your booking
        </p>
      </div>

      <div class="flex flex-col sm:flex-row gap-3">
        <RouterLink
          to="/rooms"
          class="flex-1 py-3 bg-primary-500 text-white font-semibold rounded-xl hover:bg-primary-600 transition-colors text-center"
        >
          Book Another Room
        </RouterLink>
        <RouterLink
          to="/rooms/my"
          class="flex-1 py-3 bg-gray-100 text-gray-700 font-semibold rounded-xl hover:bg-gray-200 transition-colors text-center"
        >
          My Room Bookings
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { format } from 'date-fns'

const route = useRoute()

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  try {
    return format(new Date(dateStr), 'EEEE, MMMM d, yyyy')
  } catch {
    return dateStr
  }
}
</script>
