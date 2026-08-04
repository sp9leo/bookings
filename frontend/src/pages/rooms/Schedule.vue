<template>
  <div class="max-w-full mx-auto px-4 py-6">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">Daily Schedule</h1>
      <p class="text-gray-500">View and book available rooms</p>
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-gray-50">
        <button
          @click="navigateDay('prev')"
          class="p-2 hover:bg-gray-200 rounded-lg transition-colors"
        >
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        <div class="text-center">
          <h2 class="text-lg font-semibold text-gray-900">{{ formattedDate }}</h2>
          <button
            v-if="!isToday"
            @click="goToToday"
            class="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            This Week
          </button>
        </div>

        <button
          @click="navigateDay('next')"
          class="p-2 hover:bg-gray-200 rounded-lg transition-colors"
        >
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>

      <div class="overflow-x-auto">
        <div class="min-w-[1000px]">
          <div class="flex">
            <div class="w-40 flex-shrink-0 px-4 py-4 bg-gray-50 border-b border-r border-gray-200">
              <span class="text-sm font-semibold text-gray-500 uppercase tracking-wider">Room</span>
            </div>
            <div class="flex-1 flex overflow-x-auto">
              <div
                v-for="time in timeSlots"
                :key="time"
                class="flex-shrink-0 w-28 px-2 py-4 bg-gray-50 border-b border-r border-gray-200 text-center"
              >
                <span class="text-sm font-semibold text-gray-700">{{ time }}</span>
              </div>
            </div>
          </div>

          <div
            v-for="room in rooms"
            :key="room.id"
            class="flex border-b border-gray-100 hover:bg-gray-50/50 transition-colors"
          >
            <div class="w-40 flex-shrink-0 px-4 py-4 bg-white border-r border-gray-200">
              <p class="font-semibold text-gray-900">{{ room.name }}</p>
              <p class="text-sm text-gray-500">{{ room.location }}</p>
            </div>
            <div class="flex-1 flex">
              <div
                v-for="time in timeSlots"
                :key="`${room.id}-${time}`"
                class="flex-shrink-0 w-28 border-r border-gray-100"
              >
                <TimeSlotCell
                  :slot="getSlot(room.id, time)"
                  @click="handleSlotClick"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="px-6 py-4 bg-gray-50 border-t border-gray-100">
        <div class="flex items-center gap-6 text-xs">
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 rounded bg-emerald-100 border-2 border-emerald-300"></div>
            <span class="text-gray-600">Available</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 rounded bg-blue-100 border-2 border-blue-300"></div>
            <span class="text-gray-600">Your Booking</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 rounded bg-gray-200"></div>
            <span class="text-gray-600">Booked</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 rounded bg-gray-100"></div>
            <span class="text-gray-600">Past</span>
          </div>
        </div>
      </div>
    </div>

    

    <BookingModal
      :show="showModal"
      :slot="selectedSlot"
      :room-name="selectedRoomName"
      :user-name="currentUser?.name || ''"
      :show-recurrence="false"
      :is-admin="authStore.isAdmin"
      :users="allUsers"
      :error="modalError"
      @confirm="handleConfirm"
      @cancel="handleCancel"
    />

    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="showCancelModal"
          class="fixed inset-0 z-50 flex items-center justify-center p-4"
        >
          <div
            class="absolute inset-0 bg-black/50"
            @click="showCancelModal = false"
          ></div>

          <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
            <h2 class="text-xl font-bold text-gray-900 mb-2">
              Your Reservation
            </h2>
            <p class="text-gray-500 mb-6">
              You have a reservation for this slot. What would you like to do?
            </p>

            <div class="bg-gray-50 rounded-xl p-4 mb-6">
              <div class="flex items-start gap-3">
                <div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center flex-shrink-0">
                  <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
                <div>
                  <p class="font-semibold text-gray-900">{{ selectedRoomName }}</p>
                  <p class="text-sm text-gray-500">{{ selectedSlot?.time }} - {{ selectedSlot?.endTime || getEndTime(selectedSlot?.time || '') }}</p>
                </div>
              </div>
            </div>

            <div class="flex gap-3">
              <button
                @click="showCancelModal = false"
                class="flex-1 py-3 bg-gray-100 text-gray-700 font-semibold rounded-xl hover:bg-gray-200 transition-colors"
              >
                Keep Booking
              </button>
              <button
                @click="handleCancelBooking"
                class="flex-1 py-3 bg-red-500 text-white font-semibold rounded-xl hover:bg-red-600 transition-colors"
              >
                Cancel Booking
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { format, isToday as checkIsToday, addDays, startOfWeek } from 'date-fns'
import { useAuthStore } from '@/stores/auth'
import { useBookingStore } from '@/stores/booking'
import TimeSlotCell from '@/components/schedule/TimeSlotCell.vue'
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
}

const bookingStore = useBookingStore()
const authStore = useAuthStore()

const rooms = computed(() => bookingStore.rooms)
const timeSlots = computed(() => bookingStore.timeSlots)
const currentUser = computed(() => authStore.currentUser)
const allUsers = computed(() => authStore.users)

const selectedSlot = ref<ScheduleSlot | null>(null)
const selectedRoomName = ref('')
const showModal = ref(false)
const showCancelModal = ref(false)
const modalError = ref('')

async function refreshDaySlots() {
  await bookingStore.fetchGlobalTimeSlots()
  const dateStr = format(bookingStore.currentScheduleDate, 'yyyy-MM-dd')
  await Promise.all(
    bookingStore.rooms.map(r => bookingStore.fetchRoomAvailableSlots(r.id, dateStr, dateStr))
  )
}

function handleVisibility() {
  if (document.visibilityState === 'visible') refreshDaySlots()
}

onMounted(async () => {
  if (bookingStore.rooms.length === 0) await bookingStore.fetchRooms()
  await bookingStore.fetchGlobalTimeSlots()
  await bookingStore.fetchSchedules()
  authStore.fetchUsers()
  await bookingStore.refreshRoomBookings()
  const weekStart = startOfWeek(new Date(), { weekStartsOn: 1 })
  const start = format(weekStart, 'yyyy-MM-dd')
  const end = format(addDays(weekStart, 60), 'yyyy-MM-dd')
  await Promise.all(
    bookingStore.rooms.map(r => bookingStore.fetchRoomAvailableSlots(r.id, start, end))
  )
})

onUnmounted(() => {
  window.removeEventListener('focus', refreshDaySlots)
  document.removeEventListener('visibilitychange', handleVisibility)
})

const currentDate = computed(() => bookingStore.currentScheduleDate)

const formattedDate = computed(() => {
  return format(currentDate.value, 'EEEE, MMMM d, yyyy')
})

const isToday = computed(() => {
  return checkIsToday(currentDate.value)
})

async function navigateDay(direction: 'prev' | 'next') {
  bookingStore.navigateScheduleDay(direction)
  const dateStr = format(bookingStore.currentScheduleDate, 'yyyy-MM-dd')
  await Promise.all(
    bookingStore.rooms.map(r => bookingStore.fetchRoomAvailableSlots(r.id, dateStr, dateStr))
  )
}

async function goToToday() {
  bookingStore.setScheduleDate(new Date())
  const dateStr = format(bookingStore.currentScheduleDate, 'yyyy-MM-dd')
  await Promise.all(
    bookingStore.rooms.map(r => bookingStore.fetchRoomAvailableSlots(r.id, dateStr, dateStr))
  )
}

function getSlot(roomId: string, time: string): ScheduleSlot {
  const dateStr = format(currentDate.value, 'yyyy-MM-dd')
  const slot = bookingStore.getScheduleSlot(roomId, dateStr, time)
  
  if (slot) {
    slot.isOwn = currentUser.value ? !!slot.myBookingRef || slot.bookedBy === currentUser.value.name : false
    return slot
  }
  
  const slotDateTime = new Date(`${dateStr}T${time}`)
  const now = new Date()
  const isPast = slotDateTime < now
  
  return {
    id: `new-${roomId}-${dateStr}-${time}`,
    roomId,
    date: dateStr,
    time,
    status: isPast ? 'past' : 'free',
    bookedCount: 0,
    capacity: 1,
    isFull: false,
  }
}

function handleSlotClick(slot: ScheduleSlot) {
  selectedSlot.value = slot
  modalError.value = ''
  const room = bookingStore.getRoomById(slot.roomId)
  selectedRoomName.value = room?.name || ''
  
  if (slot.status === 'booked' && (slot.isOwn || authStore.isAdmin)) {
    showCancelModal.value = true
  } else if (slot.status === 'free' || (slot.status === 'booked' && !slot.isFull)) {
    showModal.value = true
  }
}

function resolveUserByName(name: string): { name: string; email: string } | undefined {
  return allUsers.value.find(u => u.name === name)
}

async function handleConfirm(description: string, bookedBy: string) {
  if (!selectedSlot.value) return

  const bookedByUser = resolveUserByName(bookedBy) ?? { name: bookedBy, email: '' }
  const result = await bookingStore.bookScheduleSlot(
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

function getEndTime(time: string): string {
  if (!time) return ''
  const hour = parseInt(time.split(':')[0]) + 1
  return `${hour.toString().padStart(2, '0')}:00`
}

async function handleCancelBooking() {
  if (!selectedSlot.value || !selectedSlot.value.bookingRef) return

  await bookingStore.cancelScheduleBooking(selectedSlot.value.bookingRef)
  await bookingStore.refreshRoomBookings()
  const dateStr = format(currentDate.value, 'yyyy-MM-dd')
  await Promise.all(
    bookingStore.rooms.map(r => bookingStore.fetchRoomAvailableSlots(r.id, dateStr, dateStr))
  )

  showCancelModal.value = false
  selectedSlot.value = null
}
</script>
