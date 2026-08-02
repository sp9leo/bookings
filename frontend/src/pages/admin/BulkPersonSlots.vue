<template>
  <div class="px-4 py-6 max-w-5xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-bold text-gray-900">Bulk Assign Person Slots</h1>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-6">
      <!-- Select Teachers -->
      <div>
        <label class="block text-sm font-semibold text-gray-700 mb-2">Select Teachers</label>
        <div class="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto">
          <label v-for="item in bookingStore.items" :key="item.id" class="flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-200 hover:border-primary-300 cursor-pointer transition-colors" :class="{ 'border-primary-500 bg-primary-50': selectedItems.includes(item.id) }">
            <input type="checkbox" :value="item.id" v-model="selectedItems" class="rounded text-primary-600 focus:ring-primary-500" />
            <div class="text-sm">
              <div class="font-medium text-gray-900">{{ item.name }}</div>
              <div class="text-xs text-gray-500">{{ item.subtitle }}</div>
            </div>
          </label>
        </div>
      </div>

      <!-- Date Range -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1">From</label>
          <input type="date" v-model="dateFrom" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
        </div>
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1">To</label>
          <input type="date" v-model="dateTo" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
        </div>
      </div>

      <!-- Day Filter -->
      <div>
        <label class="block text-sm font-semibold text-gray-700 mb-2">Days of the Week</label>
        <div class="flex gap-3">
          <label v-for="day in dayOptions" :key="day.value" class="flex items-center gap-1.5 cursor-pointer">
            <input type="checkbox" :value="day.value" v-model="selectedDays" class="rounded text-primary-600 focus:ring-primary-500" />
            <span class="text-sm text-gray-700">{{ day.label }}</span>
          </label>
        </div>
      </div>

      <!-- Block params -->
      <div class="grid grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1">Start Time</label>
          <input type="time" v-model="blockStart" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
        </div>
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1">End Time</label>
          <input type="time" v-model="blockEnd" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
        </div>
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1">Slot Duration</label>
          <select v-model="slotDuration" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
            <option :value="5">5 min</option>
            <option :value="10">10 min</option>
            <option :value="15">15 min</option>
            <option :value="20">20 min</option>
            <option :value="30">30 min</option>
            <option :value="60">60 min</option>
          </select>
        </div>
      </div>

      <!-- Summary -->
      <div class="bg-gray-50 rounded-lg px-4 py-3 text-sm">
        <span class="text-gray-600">{{ selectedItems.length }} teacher{{ selectedItems.length !== 1 ? 's' : '' }} &times; </span>
        <span class="text-gray-600">{{ dateCount }} day{{ dateCount !== 1 ? 's' : '' }} &times; </span>
        <span class="text-gray-600">{{ slotsPerBlock }} slot{{ slotsPerBlock !== 1 ? 's' : '' }} per block = </span>
        <span class="font-bold text-primary-600">{{ totalSlots }} slot{{ totalSlots !== 1 ? 's' : '' }}</span>
      </div>

      <!-- Actions -->
      <div class="flex justify-end gap-3 pt-2 border-t border-gray-100">
        <button @click="reset" class="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 transition-colors">Reset</button>
        <button @click="assign" :disabled="totalSlots === 0" class="px-6 py-2 text-sm font-semibold text-white bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed rounded-lg transition-colors">
          Assign Slots
        </button>
      </div>
    </div>

    <!-- Result alert -->
    <div v-if="result !== null" class="mt-4 px-4 py-3 rounded-lg text-sm font-medium" :class="result.success ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-red-50 text-red-700 border border-red-200'">
      {{ result.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { format, addDays } from 'date-fns'
import { useBookingStore } from '@/stores/booking'

const bookingStore = useBookingStore()

const selectedItems = ref<string[]>([])
const dateFrom = ref('')
const dateTo = ref('')
const selectedDays = ref([1, 2, 3, 4, 5])
const blockStart = ref('08:00')
const blockEnd = ref('17:00')
const slotDuration = ref(30)
const result = ref<{ success: boolean; message: string } | null>(null)

const dayOptions = [
  { label: 'Mon', value: 1 },
  { label: 'Tue', value: 2 },
  { label: 'Wed', value: 3 },
  { label: 'Thu', value: 4 },
  { label: 'Fri', value: 5 },
]

function getDatesInRange(from: string, to: string, days: number[]): string[] {
  if (!from || !to) return []
  const dates: string[] = []
  let current = new Date(from + 'T00:00:00')
  const end = new Date(to + 'T00:00:00')
  while (current <= end) {
    if (days.includes(current.getDay())) {
      dates.push(format(current, 'yyyy-MM-dd'))
    }
    current = addDays(current, 1)
  }
  return dates
}

function countSubSlots(start: string, end: string, duration: number): number {
  if (!start || !end || duration <= 0) return 0
  const [sh, sm] = start.split(':').map(Number)
  const [eh, em] = end.split(':').map(Number)
  const startMin = sh * 60 + sm
  const endMin = eh * 60 + em
  return Math.max(0, Math.floor((endMin - startMin) / duration))
}

const dateCount = computed(() => {
  return getDatesInRange(dateFrom.value, dateTo.value, selectedDays.value).length
})

const slotsPerBlock = computed(() => {
  return countSubSlots(blockStart.value, blockEnd.value, slotDuration.value)
})

const totalSlots = computed(() => {
  return selectedItems.value.length * dateCount.value * slotsPerBlock.value
})

async function assign() {
  if (totalSlots.value === 0) return
  const dates = getDatesInRange(dateFrom.value, dateTo.value, selectedDays.value)
  const count = await bookingStore.bulkAddPersonSlots(selectedItems.value, dates, blockStart.value, blockEnd.value, slotDuration.value)
  result.value = {
    success: count > 0,
    message: count > 0
      ? `Successfully created ${count} slot${count !== 1 ? 's' : ''}.`
      : 'No new slots created (they may already exist).',
  }
}

function reset() {
  selectedItems.value = []
  dateFrom.value = ''
  dateTo.value = ''
  selectedDays.value = [1, 2, 3, 4, 5]
  blockStart.value = '08:00'
  blockEnd.value = '17:00'
  slotDuration.value = 30
  result.value = null
}

onMounted(() => {
  bookingStore.fetchItems()
})
</script>
