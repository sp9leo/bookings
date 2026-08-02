<template>
  <button
    @click="$emit('click', { roomId, dateStr })"
    class="w-full h-full min-h-[60px] rounded-lg flex flex-col items-center justify-center gap-1 transition-all relative"
    :class="cellClasses"
  >
    <template v-if="totalSlots === 0">
      <span class="text-xs font-medium text-gray-400">No slots</span>
    </template>
    <template v-else-if="bookedCount === 0">
      <span class="text-xs font-medium text-emerald-600">Available</span>
      <span class="text-[10px] text-emerald-400">All free</span>
    </template>
    <template v-else-if="bookedCount === totalSlots">
      <span class="text-xs font-medium text-gray-500">Full</span>
      <span class="text-[10px] text-gray-400">{{ bookedCount }}/{{ totalSlots }}</span>
    </template>
    <template v-else>
      <span class="text-xs font-medium text-amber-600">{{ bookedCount }}/{{ totalSlots }}</span>
      <span class="text-[10px] text-amber-400">booked</span>
    </template>
    <div v-if="hasOwnBooking" class="absolute top-1 right-1">
      <div class="w-2 h-2 bg-primary-500 rounded-full"></div>
    </div>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  slot: {
    bookedCount: number
    totalSlots: number
    hasOwnBooking: boolean
  }
  roomName: string
  roomId: string
  dateStr: string
}>()

defineEmits<{
  (e: 'click', data: { roomId: string; dateStr: string }): void
}>()

const bookedCount = computed(() => props.slot.bookedCount)
const totalSlots = computed(() => props.slot.totalSlots)
const hasOwnBooking = computed(() => props.slot.hasOwnBooking)

const cellClasses = computed(() => {
  if (totalSlots.value === 0) {
    return 'bg-gray-50 text-gray-400 cursor-default'
  }
  if (bookedCount.value === totalSlots.value) {
    return 'bg-gray-100 text-gray-400 cursor-default'
  }
  if (hasOwnBooking.value) {
    return 'bg-blue-50 hover:bg-blue-100 cursor-pointer'
  }
  return 'bg-emerald-50 hover:bg-emerald-100 cursor-pointer'
})
</script>
