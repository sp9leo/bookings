<template>
  <div class="bg-white rounded-xl border border-gray-200 p-4">
    <div class="flex items-center justify-between mb-3">
      <button @click="previousMonth" class="p-1.5 hover:bg-gray-100 rounded-lg transition-colors text-gray-600">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <div class="text-center">
        <h3 class="text-sm font-semibold text-gray-900">{{ monthLabel }}</h3>
        <button
          v-if="selectedDate"
          @click="emit('update:selectedDate', null)"
          class="text-[11px] text-primary-600 hover:text-primary-700 font-medium"
        >
          Clear selection
        </button>
      </div>
      <button @click="nextMonth" class="p-1.5 hover:bg-gray-100 rounded-lg transition-colors text-gray-600">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>

    <div class="grid grid-cols-7 gap-1 mb-1">
      <div v-for="d in weekDays" :key="d" class="text-center text-[10px] font-medium text-gray-400 py-1">{{ d }}</div>
    </div>

    <div class="grid grid-cols-7 gap-1">
      <div v-for="(day, i) in calendarDays" :key="i" class="aspect-square">
        <button
          class="w-full h-full rounded-lg border p-1 flex flex-col items-start transition-all"
          :class="dayClasses(day)"
          @click="selectDay(day)"
        >
          <span class="text-xs font-medium leading-tight">{{ day.dayNumber }}</span>
          <span v-if="day.hasSlots" class="mt-auto space-y-0.5 w-full">
            <span v-if="day.free > 0" class="flex items-center gap-1 text-[9px] leading-none text-emerald-600 truncate">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 flex-shrink-0"></span>{{ day.free }} free
            </span>
            <span v-if="day.booked > 0" class="flex items-center gap-1 text-[9px] leading-none text-amber-600 truncate">
              <span class="w-1.5 h-1.5 rounded-full bg-amber-500 flex-shrink-0"></span>{{ day.booked }} booked
            </span>
          </span>
        </button>
      </div>
    </div>

    <div class="flex items-center gap-4 mt-3 pt-2 border-t border-gray-100 text-[10px] text-gray-500">
      <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-emerald-500 inline-block"></span>Free</span>
      <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-amber-500 inline-block"></span>Booked</span>
      <span class="ml-auto font-medium text-gray-600">{{ totalFree }} free / {{ totalBooked }} booked</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import {
  format, addMonths, subMonths, startOfMonth, endOfMonth,
  startOfWeek, endOfWeek, eachDayOfInterval, isSameMonth,
} from 'date-fns'

interface DayCell {
  date: Date
  dateStr: string
  dayNumber: number | null
  inMonth: boolean
  free: number
  booked: number
  hasSlots: boolean
}

const props = defineProps<{
  slots: { date: string; booked: number }[]
  selectedDate: string | null
  focusDate?: string | null
}>()

const emit = defineEmits<{
  (e: 'update:selectedDate', value: string | null): void
}>()

const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const calendarMonth = ref(new Date())

watch(() => props.focusDate, (v) => {
  if (v) calendarMonth.value = new Date(v + 'T00:00:00')
}, { immediate: true })

const daySummary = computed(() => {
  const map: Record<string, { free: number; booked: number }> = {}
  for (const s of props.slots) {
    if (!map[s.date]) map[s.date] = { free: 0, booked: 0 }
    if (s.booked > 0) map[s.date].booked++
    else map[s.date].free++
  }
  return map
})

const totalFree = computed(() => props.slots.filter(s => s.booked === 0).length)
const totalBooked = computed(() => props.slots.filter(s => s.booked > 0).length)

const calendarDays = computed<DayCell[]>(() => {
  const start = startOfWeek(startOfMonth(calendarMonth.value), { weekStartsOn: 1 })
  const end = endOfWeek(endOfMonth(calendarMonth.value), { weekStartsOn: 1 })

  return eachDayOfInterval({ start, end }).map(date => {
    const dateStr = format(date, 'yyyy-MM-dd')
    const summary = daySummary.value[dateStr]
    const inMonth = isSameMonth(date, calendarMonth.value)
    return {
      date,
      dateStr,
      dayNumber: inMonth ? date.getDate() : null,
      inMonth,
      free: summary?.free ?? 0,
      booked: summary?.booked ?? 0,
      hasSlots: !!summary,
    }
  })
})

const monthLabel = computed(() => format(calendarMonth.value, 'MMMM yyyy'))

function previousMonth() {
  calendarMonth.value = subMonths(calendarMonth.value, 1)
}

function nextMonth() {
  calendarMonth.value = addMonths(calendarMonth.value, 1)
}

function selectDay(day: DayCell) {
  if (!day.inMonth) return
  emit('update:selectedDate', props.selectedDate === day.dateStr ? null : day.dateStr)
}

function dayClasses(day: DayCell): string {
  const selected = props.selectedDate === day.dateStr
  if (!day.inMonth) {
    return 'border-transparent text-gray-300 pointer-events-none'
  }
  if (selected) {
    return 'border-primary-500 bg-primary-50 ring-1 ring-primary-500 cursor-pointer'
  }
  if (day.hasSlots) {
    return 'border-gray-200 bg-white hover:border-primary-300 cursor-pointer'
  }
  return 'border-gray-100 bg-gray-50 text-gray-400 hover:border-primary-300 cursor-pointer'
}
</script>
