<template>
  <div class="max-w-3xl mx-auto px-4 py-12">
    <div class="text-center mb-10">
      <h1 class="text-3xl font-bold text-gray-900 mb-3">My Room Bookings</h1>
      <p class="text-gray-600">Enter your email and booking reference to view your room reservations</p>
    </div>

    <div v-if="!submitted" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
      <form @submit.prevent="lookupBookings" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
          <input
            v-model="email"
            type="email"
            required
            placeholder="Enter your work email"
            class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Booking Reference</label>
          <input
            v-model="bookingRef"
            type="text"
            required
            placeholder="Enter your booking reference"
            maxlength="6"
            class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all uppercase tracking-wider font-mono text-center text-lg"
          />
        </div>
        <button
          type="submit"
          :disabled="!isFormValid || searching"
          class="w-full py-3 bg-primary-500 text-white font-semibold rounded-xl hover:bg-primary-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          <span v-if="searching">Searching...</span>
          <span v-else>Find My Bookings</span>
        </button>
      </form>
    </div>

    <div v-else>
      <div class="flex items-center justify-between mb-6">
        <p class="text-gray-600">
          Room bookings for <span class="font-medium text-gray-900">{{ email }}</span>
        </p>
        <button
          @click="resetSearch"
          class="text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          Search again
        </button>
      </div>

      <div v-if="bookings.length === 0" class="bg-white rounded-2xl p-12 shadow-sm border border-gray-100 text-center">
        <svg class="w-12 h-12 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">No Room Bookings Found</h3>
        <p class="text-gray-500 mb-6">No room bookings match this email and reference.</p>
        <RouterLink
          to="/rooms"
          class="inline-flex items-center gap-2 px-6 py-3 bg-primary-500 text-white font-semibold rounded-xl hover:bg-primary-600 transition-colors"
        >
          Book a Room
        </RouterLink>
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="booking in bookings"
          :key="booking.id"
          class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
        >
          <div class="flex items-start justify-between">
            <div>
              <div class="flex items-center gap-3 mb-2">
                <h3 class="font-semibold text-gray-900">{{ booking.roomName }}</h3>
                <span
                  class="px-2 py-0.5 rounded-full text-xs font-medium"
                  :class="booking.status === 'Confirmed' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
                >
                  {{ booking.status }}
                </span>
              </div>
              <div class="flex items-center gap-4 text-sm text-gray-500">
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
              <p class="text-xs text-gray-400 mt-2 font-mono">Ref: {{ booking.bookingRef }}</p>
            </div>

            <button
              v-if="booking.status === 'Confirmed'"
              @click="showCancelModal(booking)"
              class="px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>

        <div class="text-center pt-4">
          <RouterLink
            to="/rooms"
            class="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Book another room
          </RouterLink>
        </div>
      </div>
    </div>

    <div
      v-if="cancelModal.show"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      @click.self="cancelModal.show = false"
    >
      <div class="bg-white rounded-2xl p-6 max-w-md w-full">
        <h3 class="text-lg font-bold text-gray-900 mb-2">Cancel Room Booking</h3>
        <p class="text-gray-600 mb-6">
          Are you sure you want to cancel your booking for {{ cancelModal.booking?.roomName }} on {{ formatDate(cancelModal.booking?.date || '') }}?
        </p>
        <div class="flex gap-3">
          <button
            @click="cancelModal.show = false"
            class="flex-1 py-2 bg-gray-100 text-gray-700 font-medium rounded-xl hover:bg-gray-200 transition-colors"
          >
            Keep Booking
          </button>
          <button
            @click="confirmCancel"
            class="flex-1 py-2 bg-red-500 text-white font-medium rounded-xl hover:bg-red-600 transition-colors"
          >
            Cancel Booking
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { format } from 'date-fns'
import { useBookingStore } from '@/stores/booking'
import { useAuthStore } from '@/stores/auth'

const bookingStore = useBookingStore()
const authStore = useAuthStore()

const email = ref('')
const bookingRef = ref('')
const submitted = ref(false)
const searching = ref(false)
const bookings = ref<any[]>([])

const isFormValid = computed(() => {
  return email.value.includes('@') && bookingRef.value.length === 6
})

const cancelModal = reactive({
  show: false,
  booking: null as any
})

onMounted(() => {
  if (authStore.currentUser) {
    email.value = authStore.currentUser.email
  }
})

async function lookupBookings() {
  if (!isFormValid.value) return

  searching.value = true

  await bookingStore.fetchMyRoomBookings()
  const allBookings = bookingStore.getRoomBookingsByEmail(email.value)
  bookings.value = allBookings.filter(b => b.bookingRef.toUpperCase() === bookingRef.value.trim().toUpperCase())

  submitted.value = true
  searching.value = false
}

function resetSearch() {
  submitted.value = false
  email.value = ''
  bookingRef.value = ''
  bookings.value = []
}

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  try {
    return format(new Date(dateStr), 'EEE, MMM d, yyyy')
  } catch {
    return dateStr
  }
}

function showCancelModal(booking: any) {
  cancelModal.show = true
  cancelModal.booking = booking
}

async function confirmCancel() {
  if (!cancelModal.booking) return

  await bookingStore.cancelRoomBooking(cancelModal.booking.bookingRef)
  bookings.value = bookings.value.filter(b => b.bookingRef !== cancelModal.booking.bookingRef || b.status !== 'Cancelled')

  if (bookings.value.length === 0 || bookings.value.every(b => b.status === 'Cancelled')) {
    bookings.value = []
  }

  cancelModal.show = false
  cancelModal.booking = null
}
</script>
