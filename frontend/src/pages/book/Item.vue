<template>
  <div class="max-w-5xl mx-auto px-4 py-8">
    <RouterLink to="/book" class="inline-flex items-center gap-2 text-gray-600 hover:text-primary-600 transition-colors mb-6">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      <span class="text-sm font-medium">Back to list</span>
    </RouterLink>

    <div v-if="!item" class="text-center py-12">
      <p class="text-gray-500">Item not found</p>
    </div>

    <div v-else class="grid lg:grid-cols-5 gap-8">
      <div class="lg:col-span-2">
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 sticky top-6">
          <div class="flex items-start gap-4 mb-6 pb-6 border-b border-gray-100">
            <div class="w-16 h-16 bg-primary-50 rounded-xl flex items-center justify-center text-primary-600 font-semibold text-xl">
              {{ getInitials(item.name) }}
            </div>
            <div>
              <h2 class="text-xl font-bold text-gray-900">{{ item.name }}</h2>
              <p class="text-gray-500">{{ item.subtitle }}</p>
              <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700 mt-1">
                {{ item.class }}
              </span>
            </div>
          </div>

          <h3 class="font-semibold text-gray-900 mb-4">Select a Date</h3>
          <CalendarPicker
            v-model="selectedDate"
            :min-date="minDate"
            :max-date="maxDate"
            :highlight-dates="availableDates"
            @update:model-value="onDateChange"
          />

         
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
                : 'bg-gray-50 text-gray-700 hover:bg-primary-50 hover:text-primary-600'"
            >
              {{ slot.from }}
            </button>
          </div>
           <div v-if="selectedSlot" class="mt-6 p-4 bg-primary-50 rounded-xl">
            <p class="text-sm text-primary-700">
              <span class="font-medium">Selected:</span> 
              {{ formatSelectedDate }} at {{ selectedSlot.from }} - {{ selectedSlot.to }}
            </p>
          </div>

          <div v-if="selectedSlot" class="mt-8 pt-6 border-t border-gray-100">
           
            <h3 class="font-semibold text-gray-900 mb-4">Your Information</h3>
            <form @submit.prevent="submitBooking" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                <input
                  v-model="form.name"
                  type="text"
                  required
                  placeholder="Enter your name"
                  class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                <input
                  v-model="form.email"
                  type="email"
                  required
                  placeholder="Enter your email"
                  class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
                <textarea
                  v-model="form.notes"
                  rows="3"
                  placeholder="Any special requirements or notes..."
                  class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all resize-none"
                ></textarea>
              </div>
              <button
                type="submit"
                :disabled="!isFormValid || submitting"
                class="w-full py-3 bg-primary-500 text-white font-semibold rounded-xl hover:bg-primary-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-200"
              >
                <span v-if="submitting">Confirming...</span>
                <span v-else>Confirm Booking</span>
              </button>
              <p v-if="errorMsg" class="mt-4 text-sm text-red-700 bg-red-50 border border-red-200 rounded-xl px-4 py-3">
                {{ errorMsg }}
              </p>
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
import CalendarPicker from '@/components/booking/CalendarPicker.vue'

const route = useRoute()
const router = useRouter()
const bookingStore = useBookingStore()

const itemId = route.params.id as string
const item = computed(() => bookingStore.getItemById(itemId))

const selectedDate = ref<Date | null>(null)
const selectedSlot = ref<any>(null)
const submitting = ref(false)
const errorMsg = ref('')
const form = reactive({
  name: '',
  email: '',
  notes: ''
})

const today = startOfDay(new Date())
const minDate = addDays(today, 1)
const maxDate = computed(() => addDays(today, bookingStore.advanceDaysFor(itemId)))

const availableSlots = computed(() => {
  if (!selectedDate.value) return []
  const dateStr = format(selectedDate.value, 'yyyy-MM-dd')
  return bookingStore.getSlotsForItem(itemId, dateStr).filter((s: any) => s.booked < s.capacity)
})

const availableDates = computed(() => {
  const dates = new Set<string>()
  const slots = bookingStore.getSlotsForItem(itemId, null).filter((s: any) => s.booked < s.capacity)
  for (const slot of slots) {
    const d = new Date(`${slot.date}T00:00:00`)
    if (d >= minDate && d <= maxDate.value) dates.add(slot.date)
  }
  return [...dates]
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
  if (bookingStore.items.length === 0) {
    await bookingStore.fetchItems('Person')
  }
  await bookingStore.fetchBookingSettings()
  await bookingStore.fetchSlots(itemId)
})

function onDateChange() {
  selectedSlot.value = null
}

function selectSlot(slot: any) {
  selectedSlot.value = slot
  bookingStore.setSelectedSlot(slot)
  bookingStore.setSelectedItem(item.value!)
}

function isSelected(slot: any): boolean {
  return selectedSlot.value?.id === slot.id
}

function getInitials(name: string): string {
  return name.split(' ').map(n => n[0]).join('').toUpperCase()
}

async function submitBooking() {
  if (!isFormValid.value || !selectedSlot.value) return

  submitting.value = true
  errorMsg.value = ''

  try {
    const reservation = await bookingStore.createReservation(selectedSlot.value, form.name, form.email, form.notes)

    if (!reservation) {
      errorMsg.value = 'Booking failed — no confirmation received. Please try again.'
      return
    }

    router.push({
      path: '/book/confirm',
      query: {
        token: reservation.accessToken,
        ref: reservation.bookingRef,
        name: reservation.customerName,
        email: reservation.customerEmail,
        item: reservation.itemName,
        date: reservation.date,
        time: `${reservation.from} - ${reservation.to}`
      }
    })
  } catch (e) {
    errorMsg.value = e instanceof Error && e.message ? e.message : 'Booking failed — please try again.'
  } finally {
    submitting.value = false
  }
}
</script>
