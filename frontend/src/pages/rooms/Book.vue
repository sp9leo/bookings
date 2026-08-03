<template>
  <div class="max-w-5xl mx-auto px-4 py-8">
    <RouterLink to="/rooms" class="inline-flex items-center gap-2 text-gray-600 hover:text-primary-600 transition-colors mb-6">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      <span class="text-sm font-medium">Back to rooms</span>
    </RouterLink>

    <div v-if="!room" class="text-center py-12">
      <p class="text-gray-500">Room not found</p>
    </div>

    <div v-else class="grid lg:grid-cols-5 gap-8">
      <div class="lg:col-span-2">
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 sticky top-6">
          <div class="flex items-start gap-4 mb-6 pb-6 border-b border-gray-100">
            <div class="w-16 h-16 bg-primary-50 rounded-xl flex items-center justify-center text-primary-600">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <div>
              <h2 class="text-xl font-bold text-gray-900">{{ room.name }}</h2>
              <p class="text-gray-500">{{ room.location }}</p>
              <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700 mt-1">
                {{ room.capacity }} people
              </span>
            </div>
          </div>

          <div class="mb-4">
            <h4 class="text-sm font-medium text-gray-700 mb-2">Features</h4>
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

          <h3 class="font-semibold text-gray-900 mb-4">Select a Date</h3>
          <CalendarPicker
            v-model="selectedDate"
            :min-date="minDate"
            :max-date="maxDate"
            @update:model-value="onDateChange"
          />

          <div v-if="selectedRoomSlot" class="mt-6 p-4 bg-primary-50 rounded-xl">
            <p class="text-sm text-primary-700">
              <span class="font-medium">Selected:</span> 
              {{ formatSelectedDate }} at {{ selectedRoomSlot.from }} - {{ selectedRoomSlot.to }}
            </p>
          </div>
        </div>
      </div>

      <div class="lg:col-span-3">
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 class="font-semibold text-gray-900 mb-6">
            Available Times
            <span v-if="selectedDate" class="text-gray-500 font-normal">
              for {{ formatDisplayDate }}
            </span>
          </h3>

          <div v-if="!selectedDate" class="text-center py-12 text-gray-500">
            <svg class="w-12 h-12 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p>Please select a date to see available times</p>
          </div>

          <div v-else-if="availableSlots.length === 0" class="text-center py-12 text-gray-500">
            <svg class="w-12 h-12 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p>No available slots for this date</p>
          </div>

          <div v-else class="grid grid-cols-3 sm:grid-cols-4 gap-3">
            <button
              v-for="slot in availableSlots"
              :key="slot.id"
              @click="selectSlot(slot)"
              class="py-3 px-4 rounded-xl font-medium text-sm transition-all duration-200"
              :class="isSelected(slot) 
                ? 'bg-primary-500 text-white shadow-md scale-105' 
                : slot.isBooked
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-50 text-gray-700 hover:bg-primary-50 hover:text-primary-600'"
              :disabled="slot.isBooked"
            >
              {{ slot.from }}
              <span v-if="slot.isBooked" class="block text-xs opacity-75">Booked</span>
            </button>
          </div>

          <div v-if="selectedRoomSlot" class="mt-8 pt-6 border-t border-gray-100">
            <h3 class="font-semibold text-gray-900 mb-4">Your Information</h3>
            <form @submit.prevent="submitBooking" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Your Name</label>
                <input
                  v-model="form.name"
                  type="text"
                  required
                  placeholder="Enter your name"
                  class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Your Email</label>
                <input
                  v-model="form.email"
                  type="email"
                  required
                  placeholder="Enter your work email"
                  class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Meeting Title (optional)</label>
                <input
                  v-model="form.title"
                  type="text"
                  placeholder="e.g., Team Standup"
                  class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all"
                />
              </div>
              <button
                type="submit"
                :disabled="!isFormValid || submitting"
                class="w-full py-3 bg-primary-500 text-white font-semibold rounded-xl hover:bg-primary-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-200"
              >
                <span v-if="submitting">Booking...</span>
                <span v-else>Book Room</span>
              </button>
              <p v-if="errorMessage" class="mt-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{{ errorMessage }}</p>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { format, addDays, startOfDay } from 'date-fns'
import { useBookingStore } from '@/stores/booking'
import { useAuthStore } from '@/stores/auth'
import CalendarPicker from '@/components/booking/CalendarPicker.vue'

const route = useRoute()
const router = useRouter()
const bookingStore = useBookingStore()
const authStore = useAuthStore()

const roomId = route.params.id as string
const room = computed(() => bookingStore.getRoomById(roomId))

const selectedDate = ref<Date | null>(null)
const selectedRoomSlot = ref<any>(null)
const submitting = ref(false)
const errorMessage = ref('')
const form = reactive({
  name: '',
  email: '',
  title: ''
})

const today = startOfDay(new Date())
const minDate = addDays(today, 1)
const maxDate = addDays(today, 30)

const availableSlots = computed(() => {
  if (!selectedDate.value) return []
  const dateStr = format(selectedDate.value, 'yyyy-MM-dd')
  return bookingStore.getRoomSlotsForDate(roomId, dateStr)
})

const formatSelectedDate = computed(() => {
  if (!selectedDate.value) return ''
  return format(selectedDate.value, 'EEEE, MMMM d, yyyy')
})

const formatDisplayDate = computed(() => {
  if (!selectedDate.value) return ''
  return format(selectedDate.value, 'MMMM d, yyyy')
})

const isFormValid = computed(() => {
  return form.name.trim() && form.email.includes('@')
})

onMounted(async () => {
  if (bookingStore.rooms.length === 0) await bookingStore.fetchRooms()
  await bookingStore.fetchSchedules()
  await bookingStore.fetchRoomScheduleSlots(roomId, format(minDate, 'yyyy-MM-dd'), format(maxDate, 'yyyy-MM-dd'))
  if (authStore.currentUser) {
    form.name = authStore.currentUser.name
    form.email = authStore.currentUser.email
  }
})

function onDateChange() {
  selectedRoomSlot.value = null
  errorMessage.value = ''
}

function selectSlot(slot: any) {
  if (slot.isBooked) return
  selectedRoomSlot.value = slot
  errorMessage.value = ''
  bookingStore.setSelectedRoomSlot(slot)
  bookingStore.setSelectedDate(selectedDate.value)
  bookingStore.setSelectedRoom(room.value!)
}

function isSelected(slot: any): boolean {
  return selectedRoomSlot.value?.id === slot.id
}

async function submitBooking() {
  if (!isFormValid.value || !selectedRoomSlot.value) return

  submitting.value = true
  errorMessage.value = ''

  const booking = await bookingStore.createRoomBooking(selectedRoomSlot.value, form.name, form.email, form.title)

  submitting.value = false

  if (!booking) {
    errorMessage.value = bookingStore.error || 'Booking failed. Please try again.'
    return
  }

  errorMessage.value = ''

  router.push({
    path: '/rooms/confirm',
    query: {
      ref: booking.bookingRef,
      room: booking.roomName,
      date: booking.date,
      time: `${booking.from} - ${booking.to}`,
      name: booking.userName,
      email: booking.userEmail
    }
  })
}
</script>
