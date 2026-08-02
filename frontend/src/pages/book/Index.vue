<template>
  <div class="max-w-5xl mx-auto px-4 py-12">
    <div class="text-center mb-10">
      <h1 class="text-3xl font-bold text-gray-900 mb-3">Book a Session</h1>
      <p class="text-gray-600 mb-8">Select a tutor or specialist to book your session</p>
    </div>

    <div v-if="pending" class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="i in 3" :key="i" class="bg-white rounded-2xl p-6 animate-pulse">
        <div class="w-16 h-16 bg-gray-200 rounded-full mb-4"></div>
        <div class="h-5 bg-gray-200 rounded w-3/4 mb-2"></div>
        <div class="h-4 bg-gray-200 rounded w-1/2"></div>
      </div>
    </div>

    <div v-else class="gap-6 items-start" :class="groupOptions.length > 1 ? 'grid lg:grid-cols-[240px_1fr]' : ''">
      <aside v-if="groupOptions.length > 1" class="bg-white rounded-2xl border border-gray-100 shadow-sm p-3 space-y-1 lg:sticky lg:top-6">
        <button
          v-for="g in groupOptions"
          :key="g.id"
          @click="selectedGroupId = g.id"
          class="w-full flex items-center justify-between px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-150"
          :class="selectedGroupId === g.id
            ? 'bg-primary-50 text-primary-700'
            : 'text-gray-700 hover:bg-gray-50'"
        >
          <span>{{ g.name }}</span>
          <span class="text-xs" :class="selectedGroupId === g.id ? 'text-primary-400' : 'text-gray-400'">{{ g.count }}</span>
        </button>
      </aside>

      <div class="min-w-0">
        <h2 v-if="groupOptions.length > 1 && selectedGroupId" class="text-lg font-semibold text-gray-900 mb-4">{{ selectedGroupName }}</h2>
        <div v-if="groupOptions.length > 1 && !selectedGroupId" class="bg-white rounded-2xl border border-gray-100 shadow-sm p-12 text-center">
          <svg class="w-12 h-12 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h10M4 18h6" />
          </svg>
          <p class="text-gray-500 font-medium mb-8">Select a category to see available sessions</p>

          <RouterLink to="/book/my" class="group block bg-gray-50 rounded-2xl border border-gray-100 p-6 hover:bg-primary-50 hover:border-primary-200 transition-all duration-200">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 bg-white rounded-xl flex items-center justify-center text-primary-600 group-hover:bg-primary-100 transition-colors">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <div class="flex-1 text-left">
                <h3 class="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">My Reservations</h3>
                <p class="text-sm text-gray-500">View or manage your booked sessions</p>
              </div>
              <svg class="w-5 h-5 text-gray-400 group-hover:text-primary-500 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </RouterLink>
        </div>
        <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <RouterLink
            v-for="item in cardItems"
            :key="item.id"
            :to="`/book/${item.id}`"
            class="group bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-all duration-200 border border-gray-100"
          >
            <div class="flex items-start gap-4">
              <div class="w-14 h-14 bg-primary-50 rounded-xl flex items-center justify-center text-primary-600 font-semibold text-lg group-hover:bg-primary-100 transition-colors">
                {{ getInitials(item.name) }}
              </div>
              <div class="flex-1 min-w-0">
                <h3 class="font-semibold text-gray-900 mb-1 group-hover:text-primary-600 transition-colors">
                  {{ item.name }}
                </h3>
                <p class="text-sm text-gray-500 mb-3">{{ item.subtitle }}</p>
                <div class="flex items-center gap-2">
                  <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                    {{ item.class }}
                  </span>
                  <span class="text-xs text-gray-400">|</span>
                  <span class="text-xs" :class="getSlotsColor(item.slotsAvailable)">
                    {{ item.slotsAvailable }} slots available
                  </span>
                </div>
              </div>
            </div>
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useBookingStore } from '@/stores/booking'

const bookingStore = useBookingStore()

type DisplayItem = {
  id: string
  name: string
  subtitle: string
  type: string
  class: string
  slotsAvailable: number
  groupId?: string
}

const items = computed<DisplayItem[]>(() => bookingStore.items.map((item): DisplayItem => ({
  ...item,
  slotsAvailable: bookingStore.getAvailableSlotsCount(item.id)
})))

const selectedGroupId = ref<string | null>(null)

type GroupOption = { id: string; name: string; count: number }

const groupOptions = computed<GroupOption[]>(() => {
  const classes = [...new Set(items.value.map(i => i.class).filter(Boolean))] as string[]
  const options: GroupOption[] = [{ id: 'all', name: 'All Items', count: items.value.length }]
  for (const cls of classes) {
    options.push({ id: cls, name: cls, count: items.value.filter(i => i.class === cls).length })
  }
  const ungrouped = items.value.filter(i => !i.class)
  if (ungrouped.length > 0) options.push({ id: 'general', name: 'General', count: ungrouped.length })
  return options
})

const visibleItems = computed(() => {
  if (!selectedGroupId.value) return []
  if (selectedGroupId.value === 'all') return items.value
  if (selectedGroupId.value === 'general') return items.value.filter(i => !i.class)
  return items.value.filter(i => i.class === selectedGroupId.value)
})

const cardItems = computed(() => {
  return groupOptions.value.length > 1 ? visibleItems.value : items.value
})

const selectedGroupName = computed(() => {
  if (!selectedGroupId.value) return ''
  return groupOptions.value.find(g => g.id === selectedGroupId.value)?.name ?? 'All Items'
})

const pending = ref(true)

onMounted(async () => {
  await bookingStore.fetchItems('Person')
  await Promise.all(bookingStore.items.map(i => bookingStore.fetchSlots(i.id)))
  selectedGroupId.value = groupOptions.value[0]?.id ?? null
  pending.value = false
})

function getInitials(name: string): string {
  return name.split(' ').map(n => n[0]).join('').toUpperCase()
}

function getSlotsColor(count: number): string {
  if (count === 0) return 'text-red-500'
  if (count <= 2) return 'text-orange-500'
  return 'text-green-600'
}
</script>
