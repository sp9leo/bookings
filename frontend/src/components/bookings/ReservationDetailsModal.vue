<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <div
          class="absolute inset-0 bg-black/50"
          @click="emit('close')"
        ></div>

        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
          <h2 class="text-lg font-bold text-gray-900 mb-1">Booking Details</h2>
          <p v-if="subtitle" class="text-sm text-gray-500 mb-5">{{ subtitle }}</p>

          <div v-if="reservations.length === 0" class="text-center py-6 text-sm text-gray-400">
            No booking details found.
          </div>

          <div v-for="res in reservations" :key="res.id" class="border border-gray-200 rounded-xl p-4 mb-3">
            <div class="flex items-center justify-between mb-2">
              <span class="font-semibold text-gray-900">{{ res.customerName }}</span>
              <span
                class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                :class="res.status === 'Confirmed' ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'"
              >
                {{ res.status }}
              </span>
            </div>
            <p class="text-sm text-gray-500">{{ res.customerEmail }}</p>
            <p class="text-sm text-gray-500 mt-1">{{ res.itemName }}</p>
            <div v-if="res.notes" class="mt-2 pt-2 border-t border-gray-100">
              <span class="text-xs text-gray-400">Notes</span>
              <p class="text-sm text-gray-700 mt-0.5 whitespace-pre-wrap">{{ res.notes }}</p>
            </div>
            <div class="mt-2 pt-2 border-t border-gray-100 flex items-center justify-between">
              <span class="text-xs text-gray-400">Reference</span>
              <span class="font-mono text-sm bg-gray-100 px-2 py-0.5 rounded">{{ res.bookingRef }}</span>
            </div>
          </div>

          <button
            @click="emit('close')"
            class="w-full mt-2 py-3 bg-gray-100 text-gray-700 font-semibold rounded-xl hover:bg-gray-200 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
defineProps<{
  show: boolean
  subtitle?: string
  reservations: any[]
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()
</script>
