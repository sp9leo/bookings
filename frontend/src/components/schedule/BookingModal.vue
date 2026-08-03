<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <div
          class="absolute inset-0 bg-black/50"
          @click="$emit('cancel')"
        ></div>

        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-2xl p-6">
          <h2 class="text-xl font-bold text-gray-900 mb-6">
            Confirm Booking
          </h2>

          <div class="grid grid-cols-2 gap-6">
            <!-- Left: Info + Description -->
            <div>
              <div class="bg-gray-50 rounded-xl p-4 mb-4">
                <div class="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p class="text-xs text-gray-500 mb-1">Room</p>
                    <p class="font-semibold text-gray-900">{{ roomName }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500 mb-1">Date</p>
                    <p class="font-semibold text-gray-900">{{ formattedDate }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500 mb-1">Time</p>
                    <p class="font-semibold text-gray-900">{{ time }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500 mb-1">Booked by</p>
                    <select
                      v-if="isAdmin"
                      v-model="bookedBy"
                      class="w-full px-2 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
                    >
                      <option v-for="u in users" :key="u.id" :value="u.name">{{ u.name }}</option>
                    </select>
                    <p v-else class="font-semibold text-gray-900">{{ userName }}</p>
                  </div>
                </div>

                <label class="block text-xs font-medium text-gray-600 mb-1">Description (optional)</label>
                <textarea
                  v-model="description"
                  rows="3"
                  placeholder="Add a description for this booking..."
                  class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                ></textarea>
              </div>
            </div>

            <!-- Right: Recurrence options -->
            <div v-if="showRecurrence" class="border-l border-gray-100 pl-6">
              <h3 class="text-sm font-semibold text-gray-700 mb-4">Recurrence</h3>

              <label class="flex items-center gap-2 mb-4 cursor-pointer select-none">
                <input
                  type="checkbox"
                  v-model="enableRecurrence"
                  class="w-4 h-4 rounded border-gray-300 text-primary-500 focus:ring-primary-100"
                />
                <span class="text-sm font-medium text-gray-700">Repeat</span>
              </label>

              <template v-if="enableRecurrence">
                <div class="flex gap-2 mb-3">
                  <label
                    v-for="freq in frequencies"
                    :key="freq.value"
                    class="flex-1"
                  >
                    <input
                      type="radio"
                      :value="freq.value"
                      v-model="recurrenceFrequency"
                      class="sr-only peer"
                    />
                    <div class="text-center py-2 rounded-lg border border-gray-200 text-sm font-medium text-gray-600 peer-checked:border-primary-500 peer-checked:text-primary-600 peer-checked:bg-primary-50 cursor-pointer transition-colors">
                      {{ freq.label }}
                    </div>
                  </label>
                </div>

                <div class="flex items-center gap-2 mb-3 text-sm">
                  <span class="text-gray-600">Every</span>
                  <input
                    type="number"
                    v-model.number="recurrenceInterval"
                    min="1"
                    max="12"
                    class="w-16 px-2 py-1.5 rounded-lg border border-gray-200 text-center text-sm outline-none focus:border-primary-500"
                  />
                  <span class="text-gray-600">{{ intervalLabel }}</span>
                </div>

                <div class="flex items-center gap-2 text-sm">
                  <span class="text-gray-600">Until</span>
                  <input
                    type="date"
                    v-model="recurrenceUntilDate"
                    class="flex-1 px-3 py-1.5 rounded-lg border border-gray-200 text-sm outline-none focus:border-primary-500"
                  />
                </div>
              </template>
            </div>
          </div>

          <div class="flex gap-3 mt-6 pt-4 border-t border-gray-100">
            <button
              @click="$emit('cancel')"
              class="flex-1 py-3 bg-gray-100 text-gray-700 font-semibold rounded-xl hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              @click="confirm"
              :disabled="submitting"
              class="flex-1 py-3 bg-primary-500 text-white font-semibold rounded-xl hover:bg-primary-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              <span v-if="submitting">
                <svg class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </span>
              <span v-else>Confirm</span>
            </button>
          </div>
          <p v-if="error" class="mt-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{{ error }}</p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { format } from 'date-fns'

interface RecurrenceConfig {
  frequency: 'daily' | 'weekly' | 'monthly'
  interval: number
  untilDate: string
}

interface ScheduleSlot {
  id: string
  roomId: string
  date: string
  time: string
  status: 'free' | 'booked' | 'past'
  bookedBy?: string
  bookingRef?: string
}

const props = withDefaults(defineProps<{
  show: boolean
  slot: ScheduleSlot | null
  roomName: string
  userName: string
  showRecurrence?: boolean
  isAdmin?: boolean
  users?: { id: string; name: string; email: string }[]
  error?: string
}>(), {
  showRecurrence: true,
  isAdmin: false,
  users: () => [],
  error: '',
})

const emit = defineEmits<{
  (e: 'confirm', description: string, bookedBy: string, recurrence?: RecurrenceConfig): void
  (e: 'cancel'): void
}>()

const description = ref('')
const bookedBy = ref('')
const submitting = ref(false)

const enableRecurrence = ref(false)
const recurrenceFrequency = ref<'daily' | 'weekly' | 'monthly'>('weekly')
const recurrenceInterval = ref(1)
const recurrenceUntilDate = ref('')

const frequencies = [
  { value: 'daily' as const, label: 'Daily' },
  { value: 'weekly' as const, label: 'Weekly' },
  { value: 'monthly' as const, label: 'Monthly' },
]

const intervalLabel = computed(() => {
  if (recurrenceFrequency.value === 'daily') return recurrenceInterval.value === 1 ? 'day' : 'days'
  if (recurrenceFrequency.value === 'weekly') return recurrenceInterval.value === 1 ? 'week' : 'weeks'
  return recurrenceInterval.value === 1 ? 'month' : 'months'
})

const formattedDate = computed(() => {
  if (!props.slot) return ''
  try {
    return format(new Date(props.slot.date), 'EEEE, MMMM d, yyyy')
  } catch {
    return props.slot.date
  }
})

const time = computed(() => {
  if (!props.slot) return ''
  const hour = parseInt(props.slot.time.split(':')[0])
  const endHour = (hour + 1).toString().padStart(2, '0')
  return `${props.slot.time} - ${endHour}:00`
})

function setDefaultUntil() {
  const d = new Date()
  d.setDate(d.getDate() + 28)
  return format(d, 'yyyy-MM-dd')
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    description.value = ''
    bookedBy.value = props.userName
    submitting.value = false
    enableRecurrence.value = false
    recurrenceFrequency.value = 'weekly'
    recurrenceInterval.value = 1
    recurrenceUntilDate.value = setDefaultUntil()
  }
})

async function confirm() {
  submitting.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  const recurrence = enableRecurrence.value
    ? { frequency: recurrenceFrequency.value, interval: recurrenceInterval.value, untilDate: recurrenceUntilDate.value }
    : undefined
  emit('confirm', description.value, bookedBy.value, recurrence)
  submitting.value = false
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-active > div:last-child,
.modal-leave-active > div:last-child {
  transition: transform 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from > div:last-child,
.modal-leave-to > div:last-child {
  transform: scale(0.95);
}
</style>
