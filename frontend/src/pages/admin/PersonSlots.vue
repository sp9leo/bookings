<template>
  <div class="px-4 py-6 max-w-5xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-bold text-gray-900">{{ isAdmin ? 'Person Slot Management' : 'My Availability Slots' }}</h1>
    </div>

    <!-- Teacher selector -->
    <div class="mb-6">
      <div v-if="isAdmin">
        <div v-if="selectedPerson" class="text-sm text-gray-600 mb-2">
          Managing slots for <strong>{{ selectedPerson.name }}</strong>
        </div>
        <select v-model="selectedItemId" class="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 w-64">
          <option value="">— Select a person —</option>
          <option v-for="item in otherUsersItems" :key="item.id" :value="item.id">{{ item.name }} ({{ item.subtitle }})</option>
        </select>
      </div>
    </div>

    <!-- Empty: no items -->
    <div v-if="!isAdmin && myItems.length === 0" class="bg-white rounded-xl border border-gray-200 p-8 text-center">
      <p class="text-sm text-gray-400">You don't have any tutoring items assigned.</p>
    </div>

    <!-- Empty: no selection -->
    <div v-else-if="!selectedItemId" class="bg-white rounded-xl border border-gray-200 p-8 text-center">
      <p class="text-sm text-gray-400">Select a person above to manage their available time slots.</p>
    </div>

    <template v-else>
      <!-- Block form -->
      <div class="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <h2 class="text-sm font-semibold text-gray-700 mb-4">Add Availability Block</h2>
        <div class="grid grid-cols-5 gap-3 items-end">
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">Date</label>
            <input type="date" v-model="blockDate" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">Start</label>
            <input type="time" v-model="blockStart" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">End</label>
            <input type="time" v-model="blockEnd" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">Slot Duration</label>
            <select v-model="blockDuration" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
              <option :value="5">5 min</option>
              <option :value="10">10 min</option>
              <option :value="15">15 min</option>
              <option :value="20">20 min</option>
              <option :value="30">30 min</option>
              <option :value="60">60 min</option>
            </select>
          </div>
          <button @click="addBlock" :disabled="!canAddBlock" class="px-4 py-2 bg-primary-500 text-white text-sm font-semibold rounded-lg hover:bg-primary-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors">
            Add Block
          </button>
        </div>
        <p v-if="selectedDateStr" class="mt-3 text-xs text-gray-500">
          Calendar date <strong>{{ formatDateHeader(selectedDateStr) }}</strong> is pre-filled above.
        </p>
      </div>

      <!-- Calendar + list side-by-side -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        <!-- Calendar overview -->
        <div class="lg:sticky lg:top-6">
          <PersonSlotsCalendar
            :slots="allSlots"
            :selected-date="selectedDateStr"
            :focus-date="firstSlotDate"
            @update:selected-date="onCalendarSelect"
          />
        </div>

        <!-- Slots list -->
        <div>
          <div v-if="filteredSlots.length === 0" class="bg-white rounded-xl border border-gray-200 p-8 text-center">
            <p class="text-sm text-gray-400">
              {{ selectedDateStr ? 'No slots on this date.' : 'No slots defined yet. Add an availability block above.' }}
            </p>
          </div>

          <template v-else>
            <!-- Day focus bar -->
            <div v-if="selectedDateStr" class="flex items-center justify-between mb-3 px-1">
              <div>
                <h3 class="text-sm font-semibold text-gray-800">{{ formatDateHeader(selectedDateStr) }}</h3>
                <p class="text-xs text-gray-400">{{ filteredSlots.length }} slot{{ filteredSlots.length !== 1 ? 's' : '' }} on this day</p>
              </div>
              <button @click="clearDateFilter" class="text-xs font-medium text-primary-600 hover:text-primary-700 transition-colors">
                Show all days
              </button>
            </div>

            <!-- Summary bar when showing all days -->
            <div v-else class="flex items-center justify-between mb-3 px-1">
              <p class="text-sm font-semibold text-gray-800">All Days</p>
              <p class="text-xs text-gray-400">{{ allSlots.length }} slots across {{ groupedSlotsCount }} day{{ groupedSlotsCount !== 1 ? 's' : '' }} — click a date on the calendar to focus</p>
            </div>

            <div v-for="(group, dateStr) in groupedSlots" :key="dateStr" class="mb-6">
              <div class="flex items-center justify-between mb-2 px-1">
                <h3 class="text-sm font-semibold text-gray-800">{{ formatDateHeader(dateStr) }}</h3>
                <span class="text-xs text-gray-400">{{ group.length }} slot{{ group.length !== 1 ? 's' : '' }}</span>
              </div>
              <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="bg-gray-50 text-left">
                      <th class="px-4 py-2.5 font-semibold text-gray-600">Time</th>
                      <th class="px-4 py-2.5 font-semibold text-gray-600">Status</th>
                      <th class="px-4 py-2.5 font-semibold text-gray-600 w-24">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="slot in group" :key="slot.id" class="border-t border-gray-100 hover:bg-gray-50">
                      <td class="px-4 py-2.5 font-medium text-gray-900">{{ slot.from }} – {{ slot.to }}</td>
                      <td class="px-4 py-2.5">
                        <div v-if="slot.booked > 0" class="flex items-center gap-2">
                          <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700">
                            Booked
                          </span>
                          <button @click="openBooking(slot)" class="text-xs font-medium text-primary-600 hover:text-primary-700 underline underline-offset-2 transition-colors">
                            View booking
                          </button>
                        </div>
                        <span v-else class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700">
                          Free
                        </span>
                      </td>
                      <td class="px-4 py-2.5">
                        <button @click="confirmDelete(slot)" class="px-2 py-1 text-xs text-red-500 border border-red-200 rounded hover:bg-red-50 disabled:opacity-30" :disabled="slot.booked > 0" :title="slot.booked > 0 ? 'Cannot delete: has active booking' : 'Delete slot'">
                          Delete
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </template>
        </div>
      </div>
    </template>

    <ReservationDetailsModal
      :show="showBookingModal"
      :reservations="selectedReservations"
      :subtitle="modalSubtitle"
      @close="showBookingModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { format, parseISO } from 'date-fns'
import { useBookingStore } from '@/stores/booking'
import { useAuthStore } from '@/stores/auth'
import PersonSlotsCalendar from '@/components/schedule/PersonSlotsCalendar.vue'
import ReservationDetailsModal from '@/components/bookings/ReservationDetailsModal.vue'

const bookingStore = useBookingStore()
const authStore = useAuthStore()

const isAdmin = computed(() => authStore.isAdmin)

const myItems = computed(() => {
  if (isAdmin.value) return bookingStore.items
  return bookingStore.items.filter(i => i.userId === authStore.currentUser?.id)
})

const otherUsersItems = computed(() => {
  if (!isAdmin.value) return myItems.value
  const currentUserId = authStore.currentUser?.id
  return myItems.value.filter(i => i.userId !== currentUserId)
})

const selectedPerson = computed(() =>
  myItems.value.find(i => i.id === selectedItemId.value)
)

const selectedItemId = ref('')
const selectedDateStr = ref<string | null>(null)

const blockDate = ref('')
const blockStart = ref('')
const blockEnd = ref('')
const blockDuration = ref(30)

if (!isAdmin.value && myItems.value.length > 0) {
  selectedItemId.value = myItems.value[0].id
  autoSelectDate()
}

watch(selectedItemId, () => {
  autoSelectDate()
  if (selectedItemId.value) bookingStore.fetchSlots(selectedItemId.value)
})

onMounted(async () => {
  if (isAdmin.value) {
    await bookingStore.fetchAdminItems()
  } else {
    await bookingStore.fetchItems()
  }
  if (!isAdmin.value && !selectedItemId.value && myItems.value.length > 0) {
    selectedItemId.value = myItems.value[0].id
  }
  if (selectedItemId.value) {
    await bookingStore.fetchSlots(selectedItemId.value)
    autoSelectDate()
  }
})

function autoSelectDate() {
  const slots = bookingStore.slots
    .filter(s => s.itemId === selectedItemId.value)
    .sort((a, b) => a.date.localeCompare(b.date) || a.from.localeCompare(b.from))
  const firstDate = slots.length ? slots[0].date : null
  selectedDateStr.value = firstDate
  if (firstDate) blockDate.value = firstDate
}

const canAddBlock = computed(() =>
  selectedItemId.value && blockDate.value && blockStart.value && blockEnd.value && blockDuration.value > 0
)

const allSlots = computed(() => {
  if (!selectedItemId.value) return []
  return bookingStore.slots
    .filter(s => s.itemId === selectedItemId.value)
    .sort((a, b) => a.date.localeCompare(b.date) || a.from.localeCompare(b.from))
})

const firstSlotDate = computed(() => allSlots.value[0]?.date || '')

const filteredSlots = computed(() => {
  if (!selectedDateStr.value) return allSlots.value
  return allSlots.value.filter(s => s.date === selectedDateStr.value)
})

const groupedSlots = computed(() => {
  const groups: Record<string, typeof filteredSlots.value> = {}
  for (const slot of filteredSlots.value) {
    if (!groups[slot.date]) groups[slot.date] = []
    groups[slot.date].push(slot)
  }
  return groups
})

const groupedSlotsCount = computed(() => Object.keys(groupedSlots.value).length)

function formatDateHeader(dateStr: string) {
  const d = parseISO(dateStr)
  return format(d, 'EEEE, MMMM d, yyyy')
}

function onCalendarSelect(dateStr: string | null) {
  selectedDateStr.value = dateStr
  if (dateStr) blockDate.value = dateStr
}

function clearDateFilter() {
  selectedDateStr.value = null
}

async function addBlock() {
  if (!canAddBlock.value || !selectedItemId.value) return
  const count = await bookingStore.addPersonBlock(selectedItemId.value, blockDate.value, blockStart.value, blockEnd.value, blockDuration.value)
  if (count > 0) {
    blockDate.value = ''
    blockStart.value = ''
    blockEnd.value = ''
  }
}

async function confirmDelete(slot: { id: string; booked: number }) {
  if (slot.booked > 0) return
  const result = await bookingStore.removePersonSlot(slot.id)
  if (typeof result === 'object' && 'hasBookings' in result) {
    alert(`Cannot remove: ${result.hasBookings} active booking(s) on this slot.`)
  }
}

const showBookingModal = ref(false)
const selectedReservations = ref<any[]>([])
const modalSlot = ref<{ date: string; from: string; to: string } | null>(null)

const modalSubtitle = computed(() => {
  if (!modalSlot.value) return ''
  const { date, from, to } = modalSlot.value
  return `${formatDateHeader(date)} · ${from} – ${to}`
})

function openBooking(slot: { id: string; date: string; from: string; to: string }) {
  modalSlot.value = { date: slot.date, from: slot.from, to: slot.to }
  selectedReservations.value = bookingStore.reservations.filter(
    r => r.slotId === slot.id && r.status === 'Confirmed'
  )
  showBookingModal.value = true
}
</script>
