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

interface RoomBooking {
  id: string
  roomSlotId: string
  roomName: string
  roomId: string
  date: string
  from: string
  to: string
  userName: string
  userEmail: string
  status: 'Confirmed' | 'Cancelled'
  bookingRef: string
}

const props = defineProps<{
  bookings: RoomBooking[]
}>()

const emit = defineEmits<{
  (e: 'edit', booking: RoomBooking): void
}>()

const calendarOptions = computed(() => {
  const confirmedBookings = props.bookings.filter(b => b.status === 'Confirmed')
  
  return {
    plugins: [dayGridPlugin, timeGridPlugin],
    initialView: 'dayGridMonth',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: ''
    },
    height: 'auto',
    events: confirmedBookings.map(booking => ({
      id: booking.bookingRef,
      title: booking.roomName,
      start: `${booking.date}T${booking.from}`,
      end: `${booking.date}T${booking.to}`,
      backgroundColor: '#10b981',
      borderColor: '#059669',
      textColor: '#ffffff',
      extendedProps: {
        booking
      }
    })),
    eventClick: (info: any) => {
    const booking = info.event.extendedProps.booking
    emit('edit', booking)
  },
  eventContent: (arg: any) => {
    return {
      html: `<div class="fc-event-custom p-1 text-xs truncate">
        <span class="font-medium">${arg.event.title}</span>
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
