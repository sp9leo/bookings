<template>
  <div>
    <div class="flex items-center  mb-4">
      <div class="flex items-center gap-1">
        <button @click="prevWeek" class="p-1.5 hover:bg-gray-200 rounded-lg transition-colors text-gray-600">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <span class="text-sm font-semibold text-gray-900 min-w-[160px] text-center">{{ weekLabel }}</span>
        <button @click="nextWeek" class="p-1.5 hover:bg-gray-200 rounded-lg transition-colors text-gray-600">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
      <button
        @click="goCurrentWeek"
        :disabled="isCurrentWeek"
        :title="isCurrentWeek ? 'You are viewing the current week' : 'Go to current week'"
        class="p-1.5 rounded-lg transition-colors text-gray-600 hover:bg-gray-200 disabled:opacity-40 disabled:cursor-not-allowed"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      </button>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full border-collapse text-xs min-w-[700px]">
        <thead>
          <tr class="bg-gray-50">
            <th rowspan="2" class="border border-gray-200 px-2 py-1.5 text-gray-700 font-semibold w-20">Date</th>
            <th rowspan="2" class="border border-gray-200 px-2 py-1.5 text-gray-700 font-semibold w-20">Room</th>
            <th v-for="(ts, i) in timeSlots" :key="i" class="border border-gray-200 px-1.5 py-1 text-gray-700 font-semibold w-16">
              {{ formatTime(ts) }}
            </th>
          </tr>
          <tr class="bg-gray-50/50">
            <th v-for="(ts, i) in timeSlots" :key="'sub-'+i" class="border border-gray-200 px-1.5 py-0.5 text-[10px] font-normal text-gray-400">
              {{ bookingStore.timeSlotLabels[ts] || formatTime(ts) }}
            </th>
          </tr>
        </thead>
        <tbody>
          <template v-for="day in weekDays" :key="day.dateStr">
            <tr v-for="(room, roomIdx) in rooms" :key="room.id + day.dateStr" class="hover:bg-gray-50/50">
              <td v-if="roomIdx === 0" :rowspan="rooms.length" class="border border-gray-200 px-2 py-1 align-top">
                <div class="font-medium text-gray-800">{{ day.label }}</div>
                <div v-if="day.isToday" class="text-[10px] mt-0.5 bg-primary-100 text-primary-700 px-1 rounded inline-block font-medium">Today</div>
              </td>
              <td class="border border-gray-200 px-2 py-1 text-gray-600 whitespace-nowrap">{{ room.shortName }}</td>
              <td v-for="(ts, tsIdx) in timeSlots" :key="tsIdx"
                class="border border-gray-200 px-1 py-1 h-[45px] align-middle text-center cursor-pointer select-none"
                :class="cellClasses(getSlot(room.id, day.dateStr, ts))"
                :style="cellStyle(getSlot(room.id, day.dateStr, ts))"
                @click="handleClick(room.id, day.dateStr, ts)"
              >
                <template v-if="!getSlot(room.id, day.dateStr, ts) || getSlot(room.id, day.dateStr, ts)?.status === 'free'">
                  <span class="text-[10px] leading-none"></span>
                </template>
<template v-else-if="getSlot(room.id, day.dateStr, ts)?.status === 'past' && !getSlot(room.id, day.dateStr, ts)?.bookingRef">
  <span class="text-[10px] leading-none">—</span>
</template>
                <template v-else>
                  <div class="text-[12px] leading-tight font-medium truncate flex items-center gap-0.5">
                    {{ shortName(getSlot(room.id, day.dateStr, ts)?.bookedBy || '') }}
                  </div>
                  <div class="text-[9px] leading-tight text-gray-500 truncate">{{ getSlot(room.id, day.dateStr, ts)?.description || '' }}</div>
                </template>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { format, startOfWeek, addDays, addWeeks, isToday as checkIsToday } from 'date-fns'
import { useAuthStore } from '@/stores/auth'
import { useBookingStore } from '@/stores/booking'

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

const emit = defineEmits<{
  (e: 'slotClick', slot: ScheduleSlot): void
}>()

const authStore = useAuthStore()
const bookingStore = useBookingStore()
const currentUser = computed(() => authStore.currentUser)

const rooms = computed(() => bookingStore.rooms.map(r => ({
  ...r,
  shortName: r.name.replace(/^(Conference |Meeting |Training )/, '')
})))

const timeSlots = computed(() => bookingStore.timeSlots)

const currentWeekStart = ref(startOfWeek(new Date(), { weekStartsOn: 1 }))

async function refreshWeek() {
  const start = format(currentWeekStart.value, 'yyyy-MM-dd')
  const end = format(addDays(currentWeekStart.value, 6), 'yyyy-MM-dd')
  await Promise.all(
    bookingStore.rooms.map(r => bookingStore.fetchRoomScheduleSlots(r.id, start, end))
  )
}

async function prevWeek() {
  currentWeekStart.value = addWeeks(currentWeekStart.value, -1)
  await refreshWeek()
}
async function nextWeek() {
  currentWeekStart.value = addWeeks(currentWeekStart.value, 1)
  await refreshWeek()
}

const isCurrentWeek = computed(() =>
  format(startOfWeek(new Date(), { weekStartsOn: 1 }), 'yyyy-MM-dd') ===
  format(currentWeekStart.value, 'yyyy-MM-dd')
)

async function goCurrentWeek() {
  currentWeekStart.value = startOfWeek(new Date(), { weekStartsOn: 1 })
  await refreshWeek()
}

const weekDays = computed(() => {
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
  return days.map((label, i) => {
    const date = addDays(currentWeekStart.value, i)
    return {
      label: `${label} ${format(date, 'd/M')}`,
      date,
      dateStr: format(date, 'yyyy-MM-dd'),
      isToday: checkIsToday(date),
    }
  })
})

const weekLabel = computed(() => {
  const start = weekDays.value[0].date
  return `Week ${format(start, 'w')}, ${format(start, 'MMM yyyy')}`
})

function formatTime(time: string): string {
  return time ? time.slice(0, 5) : ''
}

function getSlot(roomId: string, dateStr: string, time: string): ScheduleSlot | undefined {
  return bookingStore.getScheduleSlot(roomId, dateStr, time) as (ScheduleSlot | undefined)
}

function isOwn(slot: ScheduleSlot | undefined): boolean {
  return !!slot && !!currentUser.value && slot.bookedBy === currentUser.value.name
}

function cellClasses(slot: ScheduleSlot | undefined): Record<string, boolean> {
  if (!slot) return { 'bg-emerald-20 hover:bg-emerald-100 text-emerald-600': true }
  const owned = isOwn(slot)
  const beyond = bookingStore.isBeyondAdvanceWindow(slot.roomId, slot.date)
  return {
    'bg-emerald-20 hover:bg-emerald-100 text-emerald-600  cursor-pointer': slot.status === 'free',
    'hover:brightness-95 text-black-600': slot.status === 'booked' && owned,
    'text-gray-400 cursor-not-allowed': slot.status === 'booked' && !owned && !authStore.isAdmin,
    'hover:bg-red-100 bg-gray-100 text-gray-400 cursor-not-allowed opacity-80': slot.status === 'past' || beyond,
  }
}

const userColorMap = computed(() => {
  const map: Record<string, string> = {}
  for (const u of authStore.users) {
    map[u.name] = u.color
  }
  return map
})

function shortName(name: string): string {
  const parts = name.split(' ')
  return parts.length > 1 ? `${parts[0]} ${parts[1][0]}.` : name
}

function cellStyle(slot: ScheduleSlot | undefined): Record<string, string> {
  if (!slot || slot.status !== 'booked') return {}
  const color = userColorMap.value[slot.bookedBy || '']
  if (!color) return {}
  return {
    backgroundColor: isOwn(slot) ? color + '70' : color + '20',
  }
}

function handleClick(roomId: string, dateStr: string, time: string) {
  let slot = getSlot(roomId, dateStr, time)
  if (!slot) {
    const slotDateTime = new Date(`${dateStr}T${time}`)
    if (slotDateTime < new Date()) return
    slot = { id: '', roomId, date: dateStr, time, status: 'free', bookedCount: 0, capacity: 1, isFull: false } as ScheduleSlot
  }
  if (slot.status === 'past') return
  if (bookingStore.isBeyondAdvanceWindow(slot.roomId, slot.date)) return
  if (slot.status === 'booked' && !isOwn(slot) && !authStore.isAdmin) return
  emit('slotClick', slot)
}
</script>
