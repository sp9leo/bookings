<template>
  <div class="relative h-10 flex items-center justify-center p-0.5">
    <button
      v-if="slot.status !== 'past'"
      @click="$emit('click', slot)"
      class="w-full h-full rounded font-medium text-xs transition-all duration-200 flex items-center justify-center"
      :class="getSlotClasses()"
    >
      <span v-if="slot.status === 'free' && slot.bookedCount === 0" class="text-[10px]">+</span>
      <span v-else-if="slot.isOwn" class="text-[10px]">&#10003;</span>
      <span v-else-if="slot.capacity > 1" class="truncate max-w-14 px-1 text-[9px]">
        {{ slot.bookedCount }}/{{ slot.capacity }}
      </span>
      <span v-else class="truncate max-w-14 px-1 text-[9px]">
        {{ slot.bookedBy?.split(' ')[0] }}
      </span>
    </button>
    <div
      v-else
      class="w-full h-full rounded bg-gray-50 text-gray-300 text-[10px] flex items-center justify-center"
    >
      -
    </div>
  </div>
</template>

<script setup lang="ts">
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
  periodNumber?: number
}

const props = defineProps<{
  slot: ScheduleSlot
}>()

defineEmits<{
  (e: 'click', slot: ScheduleSlot): void
}>()

function getSlotClasses() {
  if (props.slot.status === 'booked') {
    if (props.slot.isOwn) {
      return 'bg-blue-100 border-2 border-blue-300 text-blue-700 cursor-pointer hover:bg-blue-200 hover:border-blue-400'
    }
    if (!props.slot.isFull) {
      return 'bg-emerald-50 border-2 border-dashed border-emerald-300 text-emerald-700 cursor-pointer hover:bg-emerald-100 hover:border-emerald-400 hover:shadow-sm'
    }
    return 'bg-gray-200 text-gray-600 cursor-not-allowed'
  }
  return 'bg-emerald-50 border-2 border-emerald-200 text-emerald-700 hover:bg-emerald-100 hover:border-emerald-300 hover:shadow-sm'
}
</script>
