<template>
  <div class="max-w-5xl mx-auto px-4 py-8">
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">My Reservations</h1>
      <p class="text-gray-500">Manage your bookings</p>
    </div>

    <!-- Tab switcher -->
    <div v-if="isTutor" class="flex gap-2 mb-6">
      <button
        v-for="tab in sectionTabs"
        :key="tab.value"
        @click="activeSection = tab.value"
        class="px-4 py-2 text-sm font-medium rounded-lg transition-colors"
        :class="activeSection === tab.value
          ? 'bg-primary-100 text-primary-700'
          : 'text-gray-600 hover:bg-gray-100'"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Your Student Bookings -->
    <div v-if="isTutor && activeSection === 'students'">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-900">Your Student Bookings</h2>
          <span class="text-sm text-gray-500">People who booked sessions with you</span>
        </div>

        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="flex flex-col gap-4 p-4 border-b border-gray-100 lg:flex-row lg:items-center lg:justify-between">
            <div class="flex flex-wrap items-center gap-2">
              <button
                v-for="tab in filterTabs"
                :key="tab.value"
                @click="tutorActiveTab = tab.value"
                class="px-4 py-2 text-sm font-medium rounded-lg transition-colors"
                :class="tutorActiveTab === tab.value 
                  ? 'bg-green-100 text-green-700' 
                  : 'text-gray-600 hover:bg-gray-100'"
              >
                {{ tab.label }}
              </button>

              <select
                v-if="authStore.isAdmin"
                v-model="tutorFilter"
                class="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">All Tutors</option>
                <option v-for="t in tutors" :key="t.id" :value="t.id">{{ t.name }}</option>
              </select>

              <input
                v-model="studentSearch"
                type="text"
                placeholder="Search student..."
                class="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 w-52"
              />
            </div>

            <div class="flex items-center gap-3">
              <div class="flex bg-gray-100 rounded-lg p-1">
                <button
                  @click="tutorViewMode = 'list'"
                  class="px-3 py-1.5 text-sm font-medium rounded-md transition-colors"
                  :class="tutorViewMode === 'list' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>
                <button
                  @click="tutorViewMode = 'calendar'"
                  class="px-3 py-1.5 text-sm font-medium rounded-md transition-colors"
                  :class="tutorViewMode === 'calendar' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <div class="p-4">
            <div v-if="filteredTutorReservations.length === 0" class="text-center py-8 text-gray-500">
              <p>No student bookings yet</p>
            </div>
            <template v-else>
              <SessionCalendar
                v-if="tutorViewMode === 'calendar'"
                :reservations="filterForCalendar(filteredTutorReservations)"
                @view="viewSessionReservation"
              />
              <table v-else class="w-full">
                <thead class="bg-gray-50 border-b border-gray-100">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Student</th>
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Date & Time</th>
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Reference</th>
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Status</th>
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  <tr v-for="res in filteredTutorReservations" :key="res.id" class="hover:bg-gray-50">
                    <td class="px-4 py-3">
                      <div class="font-medium text-gray-900">{{ res.customerName }}</div>
                      <div class="text-sm text-gray-500">{{ res.customerEmail }}</div>
                    </td>
                    <td class="px-4 py-3 text-gray-700">
                      {{ formatDate(res.date) }} at {{ res.from }} - {{ res.to }}
                    </td>
                    <td class="px-4 py-3">
                      <span class="font-mono text-sm bg-gray-100 px-2 py-1 rounded">{{ res.bookingRef }}</span>
                    </td>
                    <td class="px-4 py-3">
                      <span
                        class="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                        :class="res.status === 'Confirmed' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
                      >
                        {{ res.status }}
                      </span>
                    </td>
                    <td class="px-4 py-3">
                      <button
                        @click="viewSessionReservation(res)"
                        class="text-xs font-medium text-primary-600 hover:text-primary-700 underline underline-offset-2 transition-colors"
                      >
                        View booking
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </template>
          </div>
        </div>

    </div>

    <!-- Room Reservations -->
    <div v-if="!isTutor || activeSection === 'rooms'">
      <div>
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-900">Room Reservations</h2>
          <span class="text-sm text-gray-500">Your room booking history</span>
        </div>

        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 border-b border-gray-100">
            <div class="flex items-center gap-2">
              <button
                v-for="tab in filterTabs"
                :key="tab.value"
                @click="roomActiveTab = tab.value"
                class="px-4 py-2 text-sm font-medium rounded-lg transition-colors"
                :class="roomActiveTab === tab.value 
                  ? 'bg-primary-100 text-primary-700' 
                  : 'text-gray-600 hover:bg-gray-100'"
              >
                {{ tab.label }}
              </button>
            </div>

            <div class="flex items-center gap-3">
              <div class="flex bg-gray-100 rounded-lg p-1">
                <button
                  @click="roomViewMode = 'list'"
                  class="px-3 py-1.5 text-sm font-medium rounded-md transition-colors"
                  :class="roomViewMode === 'list' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>
                <button
                  @click="roomViewMode = 'calendar'"
                  class="px-3 py-1.5 text-sm font-medium rounded-md transition-colors"
                  :class="roomViewMode === 'calendar' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <div class="p-4">
            <BookingsList
              v-if="roomViewMode === 'list'"
              :bookings="roomBookings"
              :filter="roomActiveTab"
              @edit="openEditModal"
              @cancel="openCancelModal"
            />

            <BookingsCalendar
              v-else
              :bookings="roomBookings"
              @edit="openEditModal"
            />
          </div>
        </div>
      </div>
    </div>

    <BookingsEditModal
      :show="showEditModal"
      :booking="selectedBooking"
      :available-slots="availableSlots"
      @close="closeEditModal"
      @save="handleSave"
      @cancel="handleCancelFromModal"
    />

    <ReservationDetailsModal
      :show="showReservationModal"
      :reservations="selectedReservation ? [selectedReservation] : []"
      :subtitle="reservationModalSubtitle"
      @close="showReservationModal = false"
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
            <h2 class="text-xl font-bold text-gray-900 mb-4">Cancel Reservation</h2>
            <p class="text-gray-600 mb-6">
              Are you sure you want to cancel this reservation? This action cannot be undone.
            </p>
            <div class="flex gap-3">
              <button
                @click="showCancelModal = false"
                class="flex-1 py-3 bg-gray-100 text-gray-700 font-semibold rounded-xl hover:bg-gray-200 transition-colors"
              >
                Keep It
              </button>
              <button
                @click="confirmCancel"
                class="flex-1 py-3 bg-red-500 text-white font-semibold rounded-xl hover:bg-red-600 transition-colors"
              >
                Cancel Reservation
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
import { format, addDays } from 'date-fns'
import { useAuthStore } from '@/stores/auth'
import { useBookingStore } from '@/stores/booking'
import BookingsList from '@/components/bookings/List.vue'
import BookingsCalendar from '@/components/bookings/Calendar.vue'
import SessionCalendar from '@/components/bookings/SessionCalendar.vue'
import BookingsEditModal from '@/components/bookings/EditModal.vue'
import ReservationDetailsModal from '@/components/bookings/ReservationDetailsModal.vue'

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

interface SessionReservation {
  id: string
  itemName: string
  date: string
  from: string
  to: string
  customerName: string
  customerEmail: string
  status: 'Confirmed' | 'Cancelled'
  bookingRef: string
}

const bookingStore = useBookingStore()
const authStore = useAuthStore()

onMounted(async () => {
  await bookingStore.fetchGlobalTimeSlots()
  await bookingStore.fetchSchedules()
  await bookingStore.fetchMyBookings()
  await refreshScheduleSlots()
})

async function refreshScheduleSlots() {
  const roomIds = new Set(bookingStore.getUserBookings.map(b => b.roomId))
  const start = format(addDays(new Date(), -30), 'yyyy-MM-dd')
  const end = format(addDays(new Date(), 60), 'yyyy-MM-dd')
  await Promise.all(
    [...roomIds].map(id => bookingStore.fetchRoomScheduleSlots(id, start, end))
  )
}

const filterTabs = [
  { label: 'All', value: 'all' },
  { label: 'Upcoming', value: 'upcoming' },
  { label: 'Past', value: 'past' },
] as const

const sectionTabs = [
  { label: 'Student Bookings', value: 'students' },
  { label: 'Room Reservations', value: 'rooms' },
]

const activeSection = ref('students')
const tutorActiveTab = ref('all')
const tutorViewMode = ref<'list' | 'calendar'>('list')
const roomActiveTab = ref<'all' | 'upcoming' | 'past'>('all')
const roomViewMode = ref<'list' | 'calendar'>('list')

const showEditModal = ref(false)
const showCancelModal = ref(false)
const showReservationModal = ref(false)
const selectedReservation = ref<SessionReservation | null>(null)
const selectedBooking = ref<RoomBooking | null>(null)
const cancelBookingRef = ref<string | null>(null)

const isTutor = computed(() => bookingStore.isCurrentUserATutor)

const tutorFilter = ref('')
const studentSearch = ref('')

const tutors = computed(() => {
  const seen = new Set<string>()
  return bookingStore.items
    .filter(i => {
      if (seen.has(i.id)) return false
      seen.add(i.id)
      return true
    })
    .map(i => ({ id: i.id, name: i.name }))
})

const tutorReservations = computed(() => {
  let res = bookingStore.getAllUserAsTutorReservations
  if (authStore.isAdmin && tutorFilter.value) {
    res = res.filter(r => r.itemId === tutorFilter.value)
  }
  if (studentSearch.value) {
    const q = studentSearch.value.toLowerCase()
    res = res.filter(r =>
      r.customerName.toLowerCase().includes(q) || r.customerEmail.toLowerCase().includes(q)
    )
  }
  return res
})

const roomBookings = computed(() => bookingStore.getUserBookings)

const filteredTutorReservations = computed(() => filterReservations(tutorReservations.value, tutorActiveTab.value))

function filterReservations(reservations: SessionReservation[], filter: string) {
  const now = new Date()
  now.setHours(0, 0, 0, 0)
  
  return reservations
    .filter(r => {
      if (filter === 'all') return true
      const bookingDate = new Date(`${r.date}T${r.from}`)
      if (filter === 'upcoming') return bookingDate >= now && r.status === 'Confirmed'
      if (filter === 'past') return bookingDate < now
      return true
    })
    .sort((a, b) => {
      if (a.status === 'Cancelled' && b.status !== 'Cancelled') return 1
      if (a.status !== 'Cancelled' && b.status === 'Cancelled') return -1
      const dateA = new Date(`${a.date}T${a.from}`)
      const dateB = new Date(`${b.date}T${b.from}`)
      return dateA.getTime() - dateB.getTime()
    })
}

function filterForCalendar(reservations: SessionReservation[]): SessionReservation[] {
  return reservations.filter(r => r.status === 'Confirmed')
}

function formatDate(dateStr: string): string {
  try {
    return format(new Date(dateStr), 'MMM d, yyyy')
  } catch {
    return dateStr
  }
}

const availableSlots = computed((): AvailableSlot[] => {
  if (!selectedBooking.value) return []
  
  return bookingStore.timeSlots.map(time => {
    const hour = parseInt(time.split(':')[0])
    const endTime = `${(hour + 1).toString().padStart(2, '0')}:00`
    
    const existingSlot = bookingStore.getScheduleSlot(
      selectedBooking.value!.roomId,
      selectedBooking.value!.date,
      time
    )
    
    const isCurrentBooking = existingSlot?.bookingRef === selectedBooking.value!.bookingRef
    
    return {
      time,
      endTime,
      isBooked: existingSlot?.status === 'booked' && !isCurrentBooking,
      bookedBy: existingSlot?.bookedBy
    }
  })
})

function viewSessionReservation(res: SessionReservation) {
  selectedReservation.value = res
  showReservationModal.value = true
}

const reservationModalSubtitle = computed(() => {
  const res = selectedReservation.value
  if (!res) return ''
  return `${formatDate(res.date)} · ${res.from} – ${res.to}`
})

function openEditModal(booking: RoomBooking) {
  selectedBooking.value = booking
  showEditModal.value = true
}

function closeEditModal() {
  showEditModal.value = false
  selectedBooking.value = null
}

function openCancelModal(booking: RoomBooking) {
  selectedBooking.value = booking
  cancelBookingRef.value = booking.bookingRef
  showCancelModal.value = true
}

async function handleSave(bookingRef: string, newTime: string) {
  await bookingStore.updateBookingTime(bookingRef, newTime)
  await refreshScheduleSlots()
  closeEditModal()
}

async function handleCancelFromModal(bookingRef: string | undefined) {
  if (!bookingRef) return
  cancelBookingRef.value = bookingRef
  showEditModal.value = false
  showCancelModal.value = true
}

async function confirmCancel() {
  if (!cancelBookingRef.value) return
  await bookingStore.cancelScheduleBooking(cancelBookingRef.value)
  await refreshScheduleSlots()
  showCancelModal.value = false
  selectedBooking.value = null
  cancelBookingRef.value = null
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
