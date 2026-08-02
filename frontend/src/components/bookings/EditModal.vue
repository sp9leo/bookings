<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <div
          class="absolute inset-0 bg-black/50"
          @click="$emit('close')"
        ></div>

        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-xl font-bold text-gray-900">
              {{ isPast ? 'Reservation Details' : 'Edit Reservation' }}
            </h2>
            <button
              @click="$emit('close')"
              class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="bg-gray-50 rounded-xl p-4 mb-6">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-xs text-gray-500 mb-1">Room</p>
                <p class="font-semibold text-gray-900">{{ booking?.roomName }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 mb-1">Date</p>
                <p class="font-semibold text-gray-900">{{ formattedDate }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 mb-1">Time</p>
                <p class="font-semibold text-gray-900">{{ booking?.from }} - {{ booking?.to }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 mb-1">Status</p>
                <span
                  class="inline-flex px-2 py-0.5 text-xs font-medium rounded-full"
                  :class="statusClass"
                >
                  {{ booking?.status }}
                </span>
              </div>
            </div>
          </div>

          <div v-if="!isPast && booking?.status === 'Confirmed'" class="mb-6">
            <h3 class="text-sm font-semibold text-gray-700 mb-3">Change Time</h3>
            <div class="space-y-2">
              <label
                v-for="slot in availableSlots"
                :key="slot.time"
                class="flex items-center p-3 rounded-lg border cursor-pointer transition-all"
                :class="selectedTime === slot.time 
                  ? 'border-primary-500 bg-primary-50' 
                  : slot.isBooked 
                    ? 'border-gray-200 bg-gray-50 opacity-50 cursor-not-allowed'
                    : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'"
              >
                <input
                  type="radio"
                  :value="slot.time"
                  v-model="selectedTime"
                  :disabled="slot.isBooked"
                  class="mr-3 text-primary-600 focus:ring-primary-500"
                />
                <span class="flex-1 font-medium" :class="selectedTime === slot.time ? 'text-primary-700' : 'text-gray-700'">
                  {{ slot.time }} - {{ slot.endTime }}
                </span>
                <span v-if="slot.isBooked" class="text-xs text-gray-500">
                  {{ slot.bookedBy }}
                </span>
                <span v-else-if="selectedTime === slot.time" class="text-xs text-primary-600 font-medium">
                  Selected
                </span>
              </label>
            </div>
          </div>

          <div class="flex gap-3">
            <button
              v-if="!isPast && booking?.status === 'Confirmed'"
              @click="$emit('cancel', booking?.bookingRef)"
              class="flex-1 py-3 bg-red-50 text-red-600 font-semibold rounded-xl hover:bg-red-100 transition-colors"
            >
              Cancel Reservation
            </button>
            <button
              v-if="!isPast && booking?.status === 'Confirmed'"
              @click="saveChanges"
              :disabled="!selectedTime || selectedTime === originalTime"
              class="flex-1 py-3 bg-primary-500 text-white font-semibold rounded-xl hover:bg-primary-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              Save Changes
            </button>
            <button
              v-else
              @click="$emit('close')"
              class="flex-1 py-3 bg-gray-100 text-gray-700 font-semibold rounded-xl hover:bg-gray-200 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
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

interface AvailableSlot {
  time: string
  endTime: string
  isBooked: boolean
  bookedBy?: string
}

const props = defineProps<{
  show: boolean
  booking: RoomBooking | null
  availableSlots: AvailableSlot[]
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save', bookingRef: string, newTime: string): void
  (e: 'cancel', bookingRef: string | undefined): void
}>()

const selectedTime = ref('')

const originalTime = computed(() => props.booking?.from || '')

const formattedDate = computed(() => {
  if (!props.booking?.date) return ''
  try {
    return format(parseISO(props.booking.date), 'EEEE, MMMM d, yyyy')
  } catch {
    return props.booking.date
  }
})

const isPast = computed(() => {
  if (!props.booking) return false
  const bookingDate = parseISO(`${props.booking.date}T${props.booking.from}`)
  return bookingDate < new Date()
})

const statusClass = computed(() => {
  if (props.booking?.status === 'Cancelled') {
    return 'bg-red-100 text-red-700'
  }
  if (isPast.value) {
    return 'bg-gray-100 text-gray-600'
  }
  return 'bg-green-100 text-green-700'
})

watch(() => props.show, (newVal) => {
  if (newVal && props.booking) {
    selectedTime.value = props.booking.from
  }
})

function saveChanges() {
  if (!selectedTime.value || selectedTime.value === originalTime.value) return
  emit('save', props.booking!.bookingRef, selectedTime.value)
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
