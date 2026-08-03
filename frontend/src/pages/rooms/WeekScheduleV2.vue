<template>
  <div class="px-2 py-4 max-w-full">
    <div class="flex items-center justify-between mb-4 px-2">
      <div>
        <h1 class="text-lg font-bold text-gray-900">Week Schedule v2</h1>
        <p class="text-xs text-gray-500">Table view — dates × school hours</p>
      </div>
      <div class="flex items-center gap-3 text-[10px] flex-wrap">
        <div class="flex items-center gap-1">
          <div class="w-3 h-3 rounded bg-emerald-50 border border-emerald-300"></div>
          <span class="text-gray-500">Free</span>
        </div>
        <div class="flex items-center gap-1">
          <div class="w-3 h-3 rounded bg-gray-50 border border-gray-200"></div>
          <span class="text-gray-500">Past</span>
        </div>
        <div class="w-px h-4 bg-gray-200"></div>
        <div v-for="u in allUsers" :key="u.name" class="flex items-center gap-1">
          <div class="w-3 h-3 rounded" :style="{ backgroundColor: u.color + '50', borderColor: u.color, borderWidth: '1px' }"></div>
          <span class="text-gray-600">{{ u.name }}</span>
        </div>
      </div>
    </div>

    <WeekTable @slot-click="handleSlotClick" />

    <BookingModal
      :show="showModal"
      :slot="selectedSlot"
      :room-name="selectedRoomName"
      :user-name="currentUser?.name || ''"
      :is-admin="authStore.isAdmin"
      :users="allUsers"
      :error="modalError"
      @confirm="handleConfirm"
      @cancel="handleCancel"
    />

    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="showEditModal"
          class="fixed inset-0 z-50 flex items-center justify-center p-4"
        >
          <div class="absolute inset-0 bg-black/50" @click="handleEditCancel"></div>
          <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-2xl p-6 max-h-[90vh] overflow-y-auto">
            <h2 class="text-xl font-bold text-gray-900 mb-4">Edit Reservation</h2>

            <div class="grid grid-cols-2 gap-6">
              <!-- Left: Info + Description + Time + Scope -->
              <div>
                <div class="bg-gray-50 rounded-xl p-4 mb-4">
                  <div class="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p class="text-xs text-gray-500 mb-1">Room</p>
                      <p class="font-semibold text-gray-900">{{ selectedRoomName }}</p>
                    </div>
                    <div>
                      <p class="text-xs text-gray-500 mb-1">Date</p>
                      <p class="font-semibold text-gray-900">{{ formattedDate }}</p>
                    </div>
                    <div>
                      <p class="text-xs text-gray-500 mb-1">Current Time</p>
                      <p class="font-semibold text-gray-900">{{ selectedSlot?.time }} - {{ selectedSlot?.endTime || getEndTime(selectedSlot?.time || '') }}</p>
                    </div>
                  </div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">Description</label>
                  <input
                    v-model="editDescription"
                    type="text"
                    class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white"
                    placeholder="What is this booking for?"
                  />

                  <label v-if="authStore.isAdmin" class="block text-xs font-medium text-gray-600 mb-1 mt-4">Booked by</label>
                  <select
                    v-if="authStore.isAdmin"
                    v-model="editBookedBy"
                    class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
                  >
                    <option v-for="u in allUsers" :key="u.id" :value="u.name">{{ u.name }}</option>
                  </select>
                </div>

                <div class="mb-4">
                  <h3 class="text-sm font-semibold text-gray-700 mb-3">Change Time</h3>
                  <div class="space-y-2 max-h-48 overflow-y-auto">
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

                <div v-if="selectedSlot?.recurringGroupId" class="border-t border-gray-100 pt-4">
                  <h3 class="text-sm font-semibold text-gray-700 mb-3">Apply changes to</h3>
                  <div class="flex gap-2">
                    <label class="flex-1 cursor-pointer">
                      <input type="radio" v-model="editScope" value="this" class="sr-only peer" />
                      <div class="text-center py-2 rounded-lg border border-gray-200 text-xs font-medium text-gray-600 cursor-pointer peer-checked:border-primary-500 peer-checked:text-primary-600 peer-checked:bg-primary-50 transition-colors">This only</div>
                    </label>
                    <label class="flex-1 cursor-pointer">
                      <input type="radio" v-model="editScope" value="future" class="sr-only peer" />
                      <div class="text-center py-2 rounded-lg border border-gray-200 text-xs font-medium text-gray-600 cursor-pointer peer-checked:border-primary-500 peer-checked:text-primary-600 peer-checked:bg-primary-50 transition-colors">This & future</div>
                    </label>
                    <label class="flex-1 cursor-pointer">
                      <input type="radio" v-model="editScope" value="all" class="sr-only peer" />
                      <div class="text-center py-2 rounded-lg border border-gray-200 text-xs font-medium text-gray-600 cursor-pointer peer-checked:border-primary-500 peer-checked:text-primary-600 peer-checked:bg-primary-50 transition-colors">All</div>
                    </label>
                  </div>
                </div>
              </div>

              <!-- Right: Recurrence options -->
              <div class="border-l border-gray-100 pl-6">
                <h3 class="text-sm font-semibold text-gray-700 mb-4">Recurrence</h3>

                <label class="flex items-center gap-2 mb-4 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    v-model="editEnableRecurrence"
                    class="w-4 h-4 rounded border-gray-300 text-primary-500 focus:ring-primary-100"
                  />
                  <span class="text-sm font-medium text-gray-700">Repeat</span>
                </label>

                <template v-if="editEnableRecurrence">
                  <div class="flex gap-2 mb-3">
                    <label
                      v-for="freq in frequencies"
                      :key="freq.value"
                      class="flex-1"
                    >
                      <input
                        type="radio"
                        :value="freq.value"
                        v-model="editRecurrenceFrequency"
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
                      v-model.number="editRecurrenceInterval"
                      min="1"
                      max="12"
                      class="w-16 px-2 py-1.5 rounded-lg border border-gray-200 text-center text-sm outline-none focus:border-primary-500"
                    />
                    <span class="text-gray-600">{{ editIntervalLabel }}</span>
                  </div>

                  <div class="flex items-center gap-2 text-sm">
                    <span class="text-gray-600">Until</span>
                    <input
                      type="date"
                      v-model="editRecurrenceUntilDate"
                      class="flex-1 px-3 py-1.5 rounded-lg border border-gray-200 text-sm outline-none focus:border-primary-500"
                    />
                  </div>
                </template>
              </div>
            </div>

            <div class="flex gap-3 mt-6 pt-4 border-t border-gray-100">
              <button @click="handleDeleteBooking" class="py-3 px-4 bg-red-500 text-white font-semibold rounded-xl hover:bg-red-600 transition-colors">Delete</button>
              <button @click="handleEditCancel" class="flex-1 py-3 bg-gray-100 text-gray-700 font-semibold rounded-xl hover:bg-gray-200 transition-colors">Cancel</button>
              <button
                @click="handleSave"
                :disabled="selectedTime === selectedSlot?.time && editDescription === (selectedSlot?.description || '') && editBookedBy === (selectedSlot?.bookedBy || '')"
                class="flex-1 py-3 bg-primary-500 text-white font-semibold rounded-xl hover:bg-primary-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { format, startOfWeek, addDays } from 'date-fns'
import { useAuthStore } from '@/stores/auth'
import { useBookingStore } from '@/stores/booking'
import WeekTable from '@/components/schedule/WeekTable.vue'
import BookingModal from '@/components/schedule/BookingModal.vue'

interface ScheduleSlot {
  id: string
  roomId: string
  date: string
  time: string
  endTime?: string
  status: 'free' | 'booked' | 'past'
  bookedCount: number
  capacity: number
  isFull: boolean
  bookedBy?: string
  bookers?: { bookingRef: string; name: string; notes?: string }[]
  description?: string
  bookingRef?: string
  myBookingRef?: string
  isOwn?: boolean
  recurringGroupId?: string
}

interface AvailableSlot {
  time: string
  endTime: string
  isBooked: boolean
  bookedBy?: string
}

const authStore = useAuthStore()
const bookingStore = useBookingStore()
const currentUser = computed(() => authStore.currentUser)
const allUsers = computed(() => authStore.users)

const showModal = ref(false)
const showEditModal = ref(false)
const modalError = ref('')
const selectedSlot = ref<ScheduleSlot | null>(null)
const selectedRoomName = ref('')
const editDescription = ref('')
const editBookedBy = ref('')
const selectedTime = ref('')
const editScope = ref<'this' | 'future' | 'all'>('this')
const editEnableRecurrence = ref(false)
const editRecurrenceFrequency = ref<'daily' | 'weekly' | 'monthly'>('weekly')
const editRecurrenceInterval = ref(1)
const editRecurrenceUntilDate = ref('')

onMounted(async () => {
  if (bookingStore.rooms.length === 0) await bookingStore.fetchRooms()
  await bookingStore.fetchGlobalTimeSlots()
  await bookingStore.fetchSchedules()
  authStore.fetchUsers()
  const weekStart = startOfWeek(new Date(), { weekStartsOn: 1 })
  const start = format(weekStart, 'yyyy-MM-dd')
  const end = format(addDays(weekStart, 60), 'yyyy-MM-dd')
  await Promise.all(
    bookingStore.rooms.map(r => bookingStore.fetchRoomAvailableSlots(r.id, start, end))
  )
})

const frequencies = [
  { value: 'daily' as const, label: 'Daily' },
  { value: 'weekly' as const, label: 'Weekly' },
  { value: 'monthly' as const, label: 'Monthly' },
]

const editIntervalLabel = computed(() => {
  if (editRecurrenceFrequency.value === 'daily') return editRecurrenceInterval.value === 1 ? 'day' : 'days'
  if (editRecurrenceFrequency.value === 'weekly') return editRecurrenceInterval.value === 1 ? 'week' : 'weeks'
  return editRecurrenceInterval.value === 1 ? 'month' : 'months'
})

function setDefaultUntil(): string {
  const d = new Date()
  d.setDate(d.getDate() + 28)
  return format(d, 'yyyy-MM-dd')
}

function handleSlotClick(slot: ScheduleSlot) {
  selectedSlot.value = slot
  modalError.value = ''
  const room = bookingStore.getRoomById(slot.roomId)
  selectedRoomName.value = room?.name || ''

  const owned = !!currentUser.value && (!!slot.myBookingRef || slot.bookedBy === currentUser.value.name)
  const editable = slot.status === 'booked' && (owned || authStore.isAdmin)
  if (editable) {
    editDescription.value = slot.description || ''
    editBookedBy.value = slot.bookedBy || currentUser.value?.name || ''
    selectedTime.value = slot.time
    editScope.value = 'this'

    const existingBooking = slot.bookingRef
      ? bookingStore.roomBookings.find(b => b.bookingRef === slot.bookingRef)
      : undefined
    const existingRecurrence = existingBooking?.recurrence
    if (existingRecurrence) {
      editEnableRecurrence.value = true
      editRecurrenceFrequency.value = existingRecurrence.frequency
      editRecurrenceInterval.value = existingRecurrence.interval
      editRecurrenceUntilDate.value = existingRecurrence.untilDate
    } else {
      editEnableRecurrence.value = false
      editRecurrenceFrequency.value = 'weekly'
      editRecurrenceInterval.value = 1
      editRecurrenceUntilDate.value = setDefaultUntil()
    }

    showEditModal.value = true
  } else if (slot.status === 'free') {
    showModal.value = true
  }
}

const availableSlots = computed((): AvailableSlot[] => {
  if (!selectedSlot.value) return []
  return bookingStore.timeSlots.map(time => {
    const hour = parseInt(time.split(':')[0])
    const endTime = `${(hour + 1).toString().padStart(2, '0')}:00`
    const existingSlot = bookingStore.getScheduleSlot(
      selectedSlot.value!.roomId,
      selectedSlot.value!.date,
      time
    )
    const isCurrentBooking = existingSlot?.bookingRef === selectedSlot.value!.bookingRef
    return {
      time,
      endTime,
      isBooked: existingSlot?.status === 'booked' && !isCurrentBooking,
      bookedBy: existingSlot?.bookedBy
    }
  })
})

function resolveUserByName(name: string): { name: string; email: string } | undefined {
  return allUsers.value.find(u => u.name === name)
}

async function handleConfirm(description: string, bookedBy: string, recurrence?: { frequency: 'daily' | 'weekly' | 'monthly'; interval: number; untilDate: string }) {
  if (!selectedSlot.value) return
  const bookedByUser = resolveUserByName(bookedBy) ?? { name: bookedBy, email: '' }
  const result = recurrence
    ? await bookingStore.bookRecurringScheduleSlot(
        selectedSlot.value.roomId,
        selectedSlot.value.date,
        selectedSlot.value.time,
        description,
        recurrence,
        bookedByUser
      )
    : await bookingStore.bookScheduleSlot(
        selectedSlot.value.roomId,
        selectedSlot.value.date,
        selectedSlot.value.time,
        description,
        bookedByUser
      )

  if (!result) {
    modalError.value = bookingStore.error || 'Booking failed. Please try again.'
    return
  }

  modalError.value = ''
  showModal.value = false
  selectedSlot.value = null
}

function handleCancel() {
  showModal.value = false
  selectedSlot.value = null
  modalError.value = ''
}

async function handleSave() {
  const slot = selectedSlot.value
  if (!slot || !slot.bookingRef) return
  const ref = slot.bookingRef

  if (selectedTime.value !== slot.time) {
    await bookingStore.updateBookingTime(ref, selectedTime.value, editScope.value)
  }

  if (editDescription.value !== (slot.description || '')) {
    await bookingStore.updateScheduleSlotDescription(ref, editDescription.value, editScope.value)
  }

  if (editBookedBy.value !== (slot.bookedBy || '')) {
    await bookingStore.updateScheduleSlotBookedBy(ref, editBookedBy.value, editScope.value)
  }

  const existingBooking = bookingStore.roomBookings.find(b => b.bookingRef === ref)
  if (existingBooking) {
    if (editEnableRecurrence.value) {
      bookingStore.updateRecurrence(ref, {
        frequency: editRecurrenceFrequency.value,
        interval: editRecurrenceInterval.value,
        untilDate: editRecurrenceUntilDate.value,
      })
    } else {
      bookingStore.updateRecurrence(ref)
    }
  }

  showEditModal.value = false
  selectedSlot.value = null
}

async function handleDeleteBooking() {
  if (!selectedSlot.value || !selectedSlot.value.bookingRef) return
  await bookingStore.cancelScheduleBooking(selectedSlot.value.bookingRef, editScope.value)
  showEditModal.value = false
  selectedSlot.value = null
}

function handleEditCancel() {
  showEditModal.value = false
  selectedSlot.value = null
}

const formattedDate = computed(() => {
  if (!selectedSlot.value?.date) return ''
  try {
    return format(new Date(selectedSlot.value.date), 'EEEE, MMMM d, yyyy')
  } catch {
    return selectedSlot.value.date
  }
})

function getEndTime(time: string): string {
  if (!time) return ''
  const hour = parseInt(time.split(':')[0]) + 1
  return `${hour.toString().padStart(2, '0')}:00`
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
