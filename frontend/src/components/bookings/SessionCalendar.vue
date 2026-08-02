<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
    <FullCalendar :options="calendarOptions" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'

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

const props = defineProps<{
  reservations: SessionReservation[]
}>()

const emit = defineEmits<{
  (e: 'view', reservation: SessionReservation): void
}>()

const calendarOptions = computed(() => {
  const confirmedReservations = props.reservations.filter(r => r.status === 'Confirmed')
  
  return {
    plugins: [dayGridPlugin, timeGridPlugin],
    initialView: 'dayGridMonth',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridDay'
    },
    height: 'auto',
    slotMinTime: '07:00:00',
    slotMaxTime: '19:00:00',
    slotEventOverlap: false,
    events: confirmedReservations.map(res => ({
      id: res.bookingRef,
      title: res.customerName,
      start: `${res.date}T${res.from}`,
      end: `${res.date}T${res.to}`,
      backgroundColor: '#10b981',
      borderColor: '#059669',
      textColor: '#ffffff',
      extendedProps: {
        reservation: res
      }
    })),
    eventClick: (info: any) => {
      const reservation = info.event.extendedProps.reservation
      emit('view', reservation)
    },
    eventContent: (arg: any) => {
      const res = arg.event.extendedProps.reservation
      return {
        html: `<div class="fc-event-custom p-1 text-xs truncate">
          <span class="font-medium">${arg.event.title}</span>
          <span class="block text-[10px] opacity-80">${res.itemName}</span>
          <span class="block text-[10px] opacity-80">${arg.timeText}</span>
        </div>`
      }
    },
    dayMaxEvents: 3,
    nowIndicator: true,
    locale: 'en'
  }
})
</script>

<style>
.fc {
  --fc-border-color: #e5e7eb;
  --fc-button-bg-color: #10b981;
  --fc-button-border-color: #10b981;
  --fc-button-hover-bg-color: #059669;
  --fc-button-hover-border-color: #059669;
  --fc-button-active-bg-color: #047857;
  --fc-button-active-border-color: #047857;
  --fc-today-bg-color: #ecfdf5;
  --fc-event-border-color: transparent;
}

.fc .fc-button {
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  padding: 0.5rem 1rem;
}

.fc .fc-button-primary:not(:disabled).fc-button-active {
  background-color: #047857;
}

.fc .fc-toolbar-title {
  font-size: 1.25rem;
  font-weight: 600;
}

.fc .fc-daygrid-day-number {
  padding: 8px;
  font-weight: 500;
}

.fc .fc-daygrid-event {
  border-radius: 4px;
  padding: 2px 4px;
  margin: 1px 2px;
  cursor: pointer;
}

.fc-event-custom {
  line-height: 1.2;
}
</style>
