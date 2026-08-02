<template>
  <div class="bg-white">
    <div class="flex items-center justify-between mb-4">
      <button 
        @click="previousMonth"
        class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        :disabled="!canGoPrevious"
      >
        <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <h4 class="font-semibold text-gray-900">{{ monthYearLabel }}</h4>
      <button 
        @click="nextMonth"
        class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
      >
        <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>

    <div class="grid grid-cols-7 gap-1 mb-2">
      <div 
        v-for="day in weekDays" 
        :key="day" 
        class="text-center text-xs font-medium text-gray-400 py-2"
      >
        {{ day }}
      </div>
    </div>

    <div class="grid grid-cols-7 gap-1">
      <div 
        v-for="(day, index) in calendarDays" 
        :key="index"
        class="aspect-square"
      >
        <button
          v-if="day.date"
          @click="selectDate(day)"
          class="w-full h-full flex flex-col items-center justify-center text-sm rounded-lg transition-all"
          :class="getDayClasses(day)"
          :disabled="day.disabled"
        >
          <span>{{ day.dayNumber }}</span>
          <span v-if="day.available" class="mt-0.5 w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
        </button>
      </div>
    </div>

    <div v-if="hasHighlights" class="mt-3 flex items-center gap-2 text-xs text-gray-500">
      <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
      <span>Has available slots</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { 
  format, 
  addMonths, 
  subMonths, 
  startOfMonth, 
  endOfMonth, 
  startOfWeek, 
  endOfWeek, 
  eachDayOfInterval,
  isSameMonth,
  isSameDay,
  isToday,
  isBefore,
  isAfter,
  startOfDay
} from 'date-fns'

interface Day {
  date: Date | null
  dayNumber: number | null
  disabled: boolean
  isPast: boolean
  available: boolean
}

const props = defineProps<{
  modelValue: Date | null
  minDate?: Date
  maxDate?: Date
  highlightDates?: string[]
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: Date | null): void
}>()

const currentMonth = ref(new Date())
const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

const monthYearLabel = computed(() => format(currentMonth.value, 'MMMM yyyy'))

const canGoPrevious = computed(() => {
  if (!props.minDate) return true
  return !isSameMonth(currentMonth.value, props.minDate)
})

const highlightSet = computed(() => {
  return new Set(props.highlightDates ?? [])
})

const hasHighlights = computed(() => highlightSet.value.size > 0)

const calendarDays = computed(() => {
  const start = startOfWeek(startOfMonth(currentMonth.value), { weekStartsOn: 1 })
  const end = endOfWeek(endOfMonth(currentMonth.value), { weekStartsOn: 1 })
  const days = eachDayOfInterval({ start, end })
  const today = startOfDay(new Date())
  
  return days.map(date => {
    const isPast = isBefore(date, today)
    const beforeMin = props.minDate ? isBefore(date, startOfDay(props.minDate)) : false
    const afterMax = props.maxDate ? isAfter(date, props.maxDate) : false
    const disabled = isPast || beforeMin || afterMax || !isSameMonth(date, currentMonth.value)
    
    return {
      date,
      dayNumber: isSameMonth(date, currentMonth.value) ? date.getDate() : null,
      disabled,
      isPast,
      available: highlightSet.value.has(format(date, 'yyyy-MM-dd'))
    }
  })
})

function previousMonth() {
  if (!canGoPrevious.value) return
  currentMonth.value = subMonths(currentMonth.value, 1)
}

function nextMonth() {
  currentMonth.value = addMonths(currentMonth.value, 1)
}

function selectDate(day: Day) {
  if (day.disabled || !day.date) return
  emit('update:modelValue', day.date)
}

function getDayClasses(day: Day) {
  if (!day.date || day.disabled) {
    if (!day.date || !isSameMonth(day.date, currentMonth.value)) {
      return 'text-transparent pointer-events-none'
    }
    return 'text-gray-300 cursor-not-allowed'
  }
  
  const isSelected = props.modelValue && isSameDay(day.date, props.modelValue)
  const isTodayDate = isToday(day.date)
  
  if (isSelected) {
    return 'bg-primary-500 text-white font-semibold'
  }
  if (isTodayDate) {
    return 'bg-primary-100 text-primary-600 font-semibold hover:bg-primary-200'
  }
  if (day.available) {
    return 'bg-emerald-50 text-emerald-700 font-semibold hover:bg-emerald-100'
  }
  return 'text-gray-700 hover:bg-gray-100'
}
</script>
