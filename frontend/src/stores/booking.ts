import { defineStore } from 'pinia'
import { addDays, addMonths, format, parseISO } from 'date-fns'
import { useAuthStore } from './auth'
import { apiGet, apiPost } from '@/composables/api'

const API = '/api/method/bookings.api'

export interface Item {
  id: string
  name: string
  subtitle: string
  type: string
  class: string
  slotsAvailable: number
  userId: string
  groupId?: string
}

export interface ItemGroup {
  id: string
  name: string
}

export interface Slot {
  id: string
  itemId: string
  date: string
  from: string
  to: string
  booked: number
  capacity: number
  isBooked?: boolean
}

export interface Room {
  id: string
  name: string
  capacity: number
  location: string
  features: string[]
}

export interface RoomSlot {
  id: string
  roomId: string
  date: string
  from: string
  to: string
  isBooked: boolean
  bookedBy?: string
}

export type Scope = 'this' | 'future' | 'all'

export interface RecurrenceConfig {
  frequency: 'daily' | 'weekly' | 'monthly'
  interval: number
  untilDate: string
}

export interface RoomBooking {
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
  notes?: string
  recurrence?: RecurrenceConfig
}

export interface Reservation {
  id: string
  slotId: string
  itemName: string
  itemId: string
  date: string
  from: string
  to: string
  customerName: string
  customerEmail: string
  status: 'Confirmed' | 'Cancelled'
  accessToken: string
  bookingRef: string
  notes?: string
}

export interface ScheduleSlot {
  id: string
  roomId: string
  date: string
  time: string
  status: 'free' | 'booked' | 'past'
  bookedBy?: string
  description?: string
  bookingRef?: string
  isOwn?: boolean
  recurringGroupId?: string
  periodNumber?: number
}

export interface SchedulePeriod {
  period_number: number
  start_time: string
  end_time: string
  label?: string
}

export interface Schedule {
  name: string
  applies_to: string
  reservation_item: string
  periods: SchedulePeriod[]
}

function timeOf(v?: string | null): string {
  if (!v) return ''
  const m = v.match(/(\d{1,2}):(\d{2})/)
  return m ? `${m[1].padStart(2, '0')}:${m[2]}` : ''
}

function dateOf(v?: string | null): string {
  if (!v) return ''
  const m = v.match(/(\d{4}-\d{2}-\d{2})/)
  return m ? m[1] : ''
}

function toEndTime(from: string): string {
  const [h, m] = from.split(':').map(Number)
  return `${String(h + 1).padStart(2, '0')}:${String(m).padStart(2, '0')}`
}

function mapItem(apiItem: any): Item {
  return {
    id: apiItem.name,
    name: apiItem.item_name || apiItem.name,
    subtitle: apiItem.subtitle || '',
    type: apiItem.item_type || '',
    class: apiItem.class || '',
    slotsAvailable: 0,
    userId: apiItem.user || '',
    groupId: apiItem.group || undefined,
  }
}

function mapRoom(apiItem: any): Room {
  const features = typeof apiItem.features === 'string' && apiItem.features.trim()
    ? apiItem.features.split(',').map((f: string) => f.trim()).filter(Boolean)
    : []
  return {
    id: apiItem.name,
    name: apiItem.item_name || apiItem.name,
    capacity: apiItem.capacity || 0,
    location: apiItem.location || '',
    features,
  }
}

function mapSlot(apiSlot: any): Slot {
  return {
    id: apiSlot.name,
    itemId: apiSlot.reservation_item,
    date: apiSlot.slot_date,
    from: timeOf(apiSlot.start_time),
    to: timeOf(apiSlot.end_time),
    booked: apiSlot.booked || 0,
    capacity: apiSlot.capacity || 1,
  }
}

function mapReservation(apiRes: any, itemNames: Map<string, string>): Reservation {
  return {
    id: apiRes.name,
    slotId: apiRes.slot || '',
    itemName: itemNames.get(apiRes.reservation_item) || '',
    itemId: apiRes.reservation_item,
    date: dateOf(apiRes.from_time),
    from: timeOf(apiRes.from_time),
    to: timeOf(apiRes.to_time),
    customerName: apiRes.customer_name,
    customerEmail: apiRes.customer_email,
    status: apiRes.status === 'Cancelled' ? 'Cancelled' : 'Confirmed',
    accessToken: apiRes.access_token || '',
    bookingRef: apiRes.booking_ref,
    notes: apiRes.notes,
  }
}

function mapRoomBooking(apiB: any, roomNames: Map<string, string>): RoomBooking {
  return {
    id: apiB.name,
    roomSlotId: apiB.schedule_slot || '',
    roomName: roomNames.get(apiB.reservation_item) || '',
    roomId: apiB.reservation_item,
    date: dateOf(apiB.from_time) || apiB.booking_date,
    from: timeOf(apiB.from_time),
    to: timeOf(apiB.to_time),
    userName: apiB.customer_name,
    userEmail: apiB.customer_email || '',
    status: apiB.status === 'Cancelled' ? 'Cancelled' : 'Confirmed',
    bookingRef: apiB.booking_ref,
    notes: apiB.notes,
  }
}

function mapScheduleSlot(apiSlot: any): ScheduleSlot {
  const slotDateTime = new Date(`${apiSlot.slot_date}T${timeOf(apiSlot.start_time)}`)
  const isPast = slotDateTime.getTime() < Date.now()
  const status: ScheduleSlot['status'] = apiSlot.status === 'Booked' ? 'booked' : isPast ? 'past' : 'free'
  return {
    id: apiSlot.name,
    roomId: apiSlot.reservation_item,
    date: apiSlot.slot_date,
    time: timeOf(apiSlot.start_time),
    status,
    bookedBy: apiSlot.booked_by || '',
    description: apiSlot.description || '',
    bookingRef: apiSlot.booking_ref || undefined,
    periodNumber: apiSlot.period_number,
  }
}

export const useBookingStore = defineStore('booking', {
  state: () => ({
    items: [] as Item[],
    groups: [] as ItemGroup[],
    slots: [] as Slot[],
    rooms: [] as Room[],
    roomSlots: [] as RoomSlot[],
    roomBookings: [] as RoomBooking[],
    reservations: [] as Reservation[],
    tutorReservations: [] as Reservation[],
    scheduleSlots: [] as ScheduleSlot[],
    schedules: [] as Schedule[],

    selectedItem: null as Item | null,
    selectedSlot: null as Slot | null,
    selectedDate: null as Date | null,
    selectedRoom: null as Room | null,
    selectedRoomSlot: null as RoomSlot | null,

    currentScheduleDate: new Date(),

    timeSlots: ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00'],

    loading: false,
    error: '',
  }),

  getters: {
    getItemById: (state) => (id: string) => {
      return state.items.find((item) => item.id === id)
    },

    getRoomById: (state) => (id: string) => {
      return state.rooms.find((room) => room.id === id)
    },

    getSlotsForItem: (state) => (itemId: string, date: string | null) => {
      let slots = state.slots.filter((slot) => slot.itemId === itemId)
      if (date) {
        slots = slots.filter((slot) => slot.date === date)
      }
      return slots
    },

    getAvailableSlotsCount: (state) => (itemId: string) => {
      return state.slots.filter((slot) => slot.itemId === itemId && slot.booked < slot.capacity).length
    },

    getRoomSlotsForDate: (state) => (roomId: string, date: string | null) => {
      if (!date) return []
      return state.timeSlots.map((time) => {
        const scheduleSlot = state.scheduleSlots.find(
          (s) => s.roomId === roomId && s.date === date && s.time === time
        )
        return {
          id: `RS-${date}-${time.replace(':', '')}-${roomId}`,
          roomId,
          date,
          from: time,
          to: toEndTime(time),
          isBooked: scheduleSlot ? scheduleSlot.status === 'booked' || scheduleSlot.status === 'past' : false,
          bookedBy: scheduleSlot?.bookedBy,
        } as RoomSlot
      })
    },

    getAvailableRoomSlotsCount: (state) => (roomId: string) => {
      return state.scheduleSlots.filter((slot) => slot.roomId === roomId && slot.status === 'free').length
    },

    getReservationsByEmail: (state) => (email: string) => {
      return state.reservations.filter((r) => r.customerEmail.toLowerCase() === email.toLowerCase())
    },

    getReservationsByEmailAndRef: (state) => (email: string, ref: string) => {
      return state.reservations.filter(
        (r) =>
          r.customerEmail.toLowerCase() === email.toLowerCase() &&
          r.bookingRef.toUpperCase() === ref.toUpperCase()
      )
    },

    getRoomBookingsByEmail: (state) => (email: string) => {
      return state.roomBookings.filter((b) => b.userEmail.toLowerCase() === email.toLowerCase())
    },

    getScheduleSlotsForDate: (state) => (date: string) => {
      return state.scheduleSlots.filter((slot) => slot.date === date)
    },

    getScheduleSlot: (state) => (roomId: string, date: string, time: string) => {
      return state.scheduleSlots.find(
        (slot) => slot.roomId === roomId && slot.date === date && slot.time === time
      )
    },

    getUserBookings: (state) => {
      const authStore = useAuthStore()
      const user = authStore.currentUser
      if (!user) return []

      const fromRoomBookings = state.roomBookings.filter(
        (b) => b.userEmail.toLowerCase() === user.email.toLowerCase()
      )

      const fromScheduleSlots: RoomBooking[] = state.scheduleSlots
        .filter((s) => s.status === 'booked' && s.bookedBy === user.name && s.bookingRef)
        .filter((s) => !state.roomBookings.some((b) => b.bookingRef === s.bookingRef))
        .map((s) => {
          const room = state.rooms.find((r) => r.id === s.roomId)
          return {
            id: s.id,
            roomSlotId: s.id,
            roomName: room?.name || 'Unknown',
            roomId: s.roomId,
            date: s.date,
            from: s.time,
            to: toEndTime(s.time),
            userName: user.name,
            userEmail: user.email,
            status: 'Confirmed' as const,
            bookingRef: s.bookingRef!,
          }
        })

      return [...fromRoomBookings, ...fromScheduleSlots]
    },

    getUserUpcomingBookings: (state) => {
      const authStore = useAuthStore()
      const email = authStore.currentUser?.email || ''
      const now = new Date()
      now.setHours(0, 0, 0, 0)
      return state.roomBookings
        .filter((b) => b.userEmail.toLowerCase() === email.toLowerCase())
        .filter((b) => {
          const bookingDate = new Date(`${b.date}T${b.from}`)
          return bookingDate >= now && b.status === 'Confirmed'
        })
        .sort((a, b) => {
          const dateA = new Date(`${a.date}T${a.from}`)
          const dateB = new Date(`${b.date}T${b.from}`)
          return dateA.getTime() - dateB.getTime()
        })
    },

    getUserPastBookings: (state) => {
      const authStore = useAuthStore()
      const email = authStore.currentUser?.email || ''
      const now = new Date()
      now.setHours(0, 0, 0, 0)
      return state.roomBookings
        .filter((b) => b.userEmail.toLowerCase() === email.toLowerCase())
        .filter((b) => {
          const bookingDate = new Date(`${b.date}T${b.from}`)
          return bookingDate < now
        })
        .sort((a, b) => {
          const dateA = new Date(`${a.date}T${a.from}`)
          const dateB = new Date(`${b.date}T${b.from}`)
          return dateB.getTime() - dateA.getTime()
        })
    },

    getUserAsTutorReservations: (state) => {
      return state.tutorReservations
    },

    getUserAsTutorUpcomingReservations: (state) => {
      const now = new Date()
      now.setHours(0, 0, 0, 0)
      return state.tutorReservations
        .filter((r) => {
          const bookingDate = new Date(`${r.date}T${r.from}`)
          return bookingDate >= now && r.status === 'Confirmed'
        })
        .sort((a, b) => {
          const dateA = new Date(`${a.date}T${a.from}`)
          const dateB = new Date(`${b.date}T${b.from}`)
          return dateA.getTime() - dateB.getTime()
        })
    },

    isCurrentUserATutor: (state) => {
      const authStore = useAuthStore()
      const userId = authStore.currentUser?.id || ''
      if (authStore.isAdmin) return true
      return state.items.some((item) => item.userId === userId)
    },

    getAllUserAsTutorReservations: (state) => {
      const authStore = useAuthStore()
      if (authStore.isAdmin) return state.reservations
      return state.tutorReservations
    },
  },

  actions: {
    getScheduleForRoom(roomId: string): Schedule | null {
      return this.schedules.find(
        (s) => s.reservation_item === roomId && (s.applies_to === 'Room' || !s.applies_to)
      ) || null
    },

    findPeriodForTime(schedule: Schedule, time: string): SchedulePeriod | null {
      return schedule.periods.find((p) => timeOf(p.start_time) === time) || null
    },

    setSelectedItem(item: Item | null) {
      this.selectedItem = item
      this.selectedSlot = null
      this.selectedDate = null
    },

    setSelectedSlot(slot: Slot | null) {
      this.selectedSlot = slot
    },

    setSelectedDate(date: Date | null) {
      this.selectedDate = date
      this.selectedSlot = null
    },

    setSelectedRoom(room: Room | null) {
      this.selectedRoom = room
      this.selectedRoomSlot = null
      this.selectedDate = null
    },

    setSelectedRoomSlot(slot: RoomSlot | null) {
      this.selectedRoomSlot = slot
    },

    setScheduleDate(date: Date) {
      this.currentScheduleDate = date
    },

    navigateScheduleDay(direction: 'prev' | 'next') {
      if (direction === 'prev') {
        this.currentScheduleDate = addDays(this.currentScheduleDate, -1)
      } else {
        this.currentScheduleDate = addDays(this.currentScheduleDate, 1)
      }
    },

    async fetchItems(itemType?: string) {
      const params = itemType ? { item_type: itemType } : undefined
      const data = (await apiGet(`${API}.get_items`, params)) as any[] | null
      this.items = (data || []).map(mapItem)
    },

    async fetchRooms() {
      const data = (await apiGet(`${API}.get_rooms`)) as any[] | null
      this.rooms = (data || []).map(mapRoom)
    },

    async fetchSlots(itemId: string, date?: string) {
      const params: Record<string, any> = { item: itemId }
      if (date) params.date = date
      const data = (await apiGet(`${API}.get_slots`, params)) as any[] | null
      const mapped = (data || []).map(mapSlot)
      this.slots = [...this.slots.filter((s) => s.itemId !== itemId), ...mapped]
    },

    async fetchSchedules() {
      const data = (await apiGet(`${API}.get_schedules`, { item_type: 'Room' })) as any[] | null
      this.schedules = (data || []).map((s) => ({
        name: s.name,
        applies_to: s.applies_to,
        reservation_item: s.reservation_item,
        periods: s.periods || [],
      }))
    },

    async fetchRoomScheduleSlots(roomId: string, startDate?: string, endDate?: string) {
      const params: Record<string, any> = { item: roomId }
      if (startDate) params.start_date = startDate
      if (endDate) params.end_date = endDate
      const data = (await apiGet(`${API}.get_schedule_for_room`, params)) as any[] | null
      const mapped = (data || []).map(mapScheduleSlot)
      this.scheduleSlots = [...this.scheduleSlots.filter((s) => s.roomId !== roomId), ...mapped]
    },

    async fetchMySessionReservations() {
      if (this.items.length === 0) await this.fetchItems()
      const itemNames = new Map(this.items.map((i) => [i.id, i.name]))
      const data = (await apiGet(`${API}.get_my_session_reservations`)) as any[] | null
      this.reservations = (data || []).map((r) => mapReservation(r, itemNames))
    },

    async fetchMyTutorBookings() {
      if (this.items.length === 0) await this.fetchItems()
      const itemNames = new Map(this.items.map((i) => [i.id, i.name]))
      const data = (await apiGet(`${API}.get_my_tutor_bookings`)) as any[] | null
      this.tutorReservations = (data || []).map((r) => mapReservation(r, itemNames))
    },

    async fetchMyRoomBookings() {
      const roomNames = new Map(this.rooms.map((r) => [r.id, r.name]))
      const data = (await apiGet(`${API}.get_my_room_bookings`)) as any[] | null
      this.roomBookings = (data || []).map((b) => mapRoomBooking(b, roomNames))
    },

    async fetchMyBookings() {
      await Promise.all([
        this.fetchMySessionReservations(),
        this.fetchMyTutorBookings(),
        this.fetchRooms(),
        this.fetchMyRoomBookings(),
      ])
    },

    async createReservation(
      slot: Slot,
      customerName: string,
      customerEmail: string,
      notes?: string
    ): Promise<Reservation | null> {
      const res = await apiPost<any>(`${API}.reserve`, {
        slot: slot.id,
        customer_name: customerName,
        customer_email: customerEmail,
        notes: notes || null,
      })
      if (!res) return null

      const item = this.getItemById(slot.itemId)
      const reservation: Reservation = {
        id: res.name || `RSV-${Date.now()}`,
        slotId: slot.id,
        itemName: item?.name || '',
        itemId: slot.itemId,
        date: slot.date,
        from: slot.from,
        to: slot.to,
        customerName,
        customerEmail,
        status: 'Confirmed',
        accessToken: res.access_token || '',
        bookingRef: res.booking_ref,
        notes,
      }

      slot.booked = (slot.booked || 0) + 1
      this.reservations.push(reservation)
      this.selectedSlot = null

      return reservation
    },

    async cancelReservation(token: string): Promise<boolean> {
      const res = await apiPost<any>(`${API}.cancel_reservation`, { access_token: token })
      const reservation = this.reservations.find((r) => r.accessToken === token)
      if (res?.success && reservation) {
        reservation.status = 'Cancelled'
        const slot = this.slots.find((s) => s.id === reservation.slotId)
        if (slot && slot.booked > 0) slot.booked--
        return true
      }
      return false
    },

    getReservationByToken(token: string): Reservation | undefined {
      return this.reservations.find((r) => r.accessToken === token)
    },

    async lookupReservation(email: string, ref: string): Promise<Reservation | null> {
      const res = await apiGet<any>(`${API}.lookup_reservation`, { email, booking_ref: ref })
      if (!res) return null
      const itemNames = new Map(this.items.map((i) => [i.id, i.name]))
      const mapped = mapReservation(res, itemNames)
      const idx = this.reservations.findIndex((r) => r.id === mapped.id)
      if (idx >= 0) this.reservations[idx] = mapped
      else this.reservations.push(mapped)
      return mapped
    },

    async bookRoomBooking(roomId: string, date: string, time: string, description: string): Promise<RoomBooking | null> {
      const schedule = this.getScheduleForRoom(roomId)
      if (!schedule) return null
      const period = this.findPeriodForTime(schedule, time)
      if (!period) return null

      const slotDoc = await apiGet<any>(`${API}.get_or_create_slot`, {
        schedule: schedule.name,
        slot_date: date,
        period_number: period.period_number,
      })
      if (!slotDoc) return null

      const res = await apiPost<any>(`${API}.book_room`, {
        schedule_slot: slotDoc.name,
        notes: description || null,
      })
      if (!res) return null

      await this.fetchRoomScheduleSlots(roomId)
      await this.fetchMyRoomBookings()

      const room = this.getRoomById(roomId)
      return {
        id: res.name,
        roomSlotId: slotDoc.name,
        roomName: room?.name || '',
        roomId,
        date,
        from: time,
        to: toEndTime(time),
        userName: useAuthStore().currentUser?.name || '',
        userEmail: useAuthStore().currentUser?.email || '',
        status: 'Confirmed',
        bookingRef: res.booking_ref,
        notes: description,
      }
    },

    async createRoomBooking(slot: RoomSlot, _userName: string, _userEmail: string): Promise<RoomBooking | null> {
      return this.bookRoomBooking(slot.roomId, slot.date, slot.from, '')
    },

    async bookScheduleSlot(
      roomId: string,
      date: string,
      time: string,
      description: string,
      _bookedBy?: { name: string; email: string }
    ): Promise<RoomBooking | null> {
      return this.bookRoomBooking(roomId, date, time, description)
    },

    async bookRecurringScheduleSlot(
      roomId: string,
      date: string,
      time: string,
      description: string,
      recurrence: RecurrenceConfig,
      _bookedBy?: { name: string; email: string }
    ): Promise<string | null> {
      const schedule = this.getScheduleForRoom(roomId)
      if (!schedule) return null
      const period = this.findPeriodForTime(schedule, time)
      if (!period) return null

      const dates: string[] = []
      let current = parseISO(date)
      const until = parseISO(recurrence.untilDate)
      let count = 0
      const maxOccurrences = recurrence.frequency === 'daily' ? 365 : recurrence.frequency === 'weekly' ? 52 : 24

      while (current <= until && count < maxOccurrences) {
        dates.push(format(current, 'yyyy-MM-dd'))
        if (recurrence.frequency === 'daily') {
          current = addDays(current, recurrence.interval)
        } else if (recurrence.frequency === 'weekly') {
          current = addDays(current, 7 * recurrence.interval)
        } else {
          current = addMonths(current, recurrence.interval)
        }
        count++
      }

      if (dates.length === 0) return null

      const res = await apiPost<any>(`${API}.create_recurring_room_bookings`, {
        schedule: schedule.name,
        dates: JSON.stringify(dates),
        period_number: period.period_number,
        notes: description || null,
      })
      if (!res?.success) return null

      await this.fetchRoomScheduleSlots(roomId)
      await this.fetchMyRoomBookings()

      const created = res.created || []
      return created.length > 0 ? created[0].booking_ref : null
    },

    async updateScheduleSlotDescription(bookingRef: string, description: string, _scope: Scope = 'this'): Promise<boolean> {
      const slot = this.scheduleSlots.find((s) => s.bookingRef === bookingRef)
      if (!slot || slot.status !== 'booked') return false
      const res = await apiPost<any>(`${API}.update_slot_details`, { slot: slot.id, description })
      if (!res?.success) return false
      slot.description = description
      return true
    },

    async updateScheduleSlotBookedBy(bookingRef: string, name: string, _scope: Scope = 'this'): Promise<boolean> {
      const slot = this.scheduleSlots.find((s) => s.bookingRef === bookingRef)
      if (!slot || slot.status !== 'booked') return false
      const res = await apiPost<any>(`${API}.update_slot_details`, { slot: slot.id, booked_by: name })
      if (!res?.success) return false
      slot.bookedBy = name
      return true
    },

    updateRecurrence(_bookingRef: string, _recurrence?: RecurrenceConfig): boolean {
      return false
    },

    async cancelScheduleBooking(bookingRef: string, _scope: Scope = 'this'): Promise<boolean> {
      const res = await apiPost<any>(`${API}.cancel_room_booking`, { booking_ref: bookingRef })
      if (!res?.success) return false
      const slot = this.scheduleSlots.find((s) => s.bookingRef === bookingRef)
      if (slot) {
        slot.status = 'free'
        slot.bookedBy = ''
        slot.bookingRef = undefined
        slot.description = ''
      }
      const booking = this.roomBookings.find((b) => b.bookingRef === bookingRef)
      if (booking) booking.status = 'Cancelled'
      return true
    },

    async cancelRoomBooking(bookingRef: string): Promise<boolean> {
      return this.cancelScheduleBooking(bookingRef)
    },

    async adminCancelBooking(bookingRef: string): Promise<boolean> {
      return this.cancelScheduleBooking(bookingRef)
    },

    async updateBookingTime(bookingRef: string, newTime: string, _scope: Scope = 'this'): Promise<RoomBooking | null> {
      const booking = this.roomBookings.find((b) => b.bookingRef === bookingRef)
      if (!booking) return null

      const res = await apiPost<any>(`${API}.update_booking_time`, {
        booking_ref: bookingRef,
        new_start_time: newTime,
        new_end_time: toEndTime(newTime),
      })
      if (!res?.success) return null

      booking.from = newTime
      booking.to = toEndTime(newTime)
      const slot = this.scheduleSlots.find((s) => s.bookingRef === bookingRef)
      if (slot) slot.time = newTime

      return booking
    },

    async fetchAdminItems() {
      const data = (await apiGet(`${API}.get_all_items`)) as any[] | null
      this.items = (data || []).map(mapItem)
    },

    async fetchGroups() {
      const data = (await apiGet(`${API}.get_groups`)) as any[] | null
      this.groups = (data || []).map((g) => ({ id: g.name, name: g.group_name }))
    },

    async addRoom(data?: Partial<Room>): Promise<Room | null> {
      const itemData: Record<string, any> = {
        item_name: data?.name,
        item_type: 'Room',
        capacity: data?.capacity || 0,
        location: data?.location || '',
        features: (data?.features || []).join(', '),
      }
      const res = await apiPost<any>(`${API}.create_item`, { data: itemData })
      if (!res?.name) return null
      await this.fetchRooms()
      return { id: res.name, name: data?.name || '', capacity: data?.capacity || 0, location: data?.location || '', features: data?.features || [] }
    },

    async updateRoom(id?: string, data?: Partial<Room>): Promise<boolean> {
      if (!id) return false
      const itemData: Record<string, any> = {}
      if (data?.name !== undefined) itemData.item_name = data.name
      if (data?.capacity !== undefined) itemData.capacity = data.capacity
      if (data?.location !== undefined) itemData.location = data.location
      if (data?.features !== undefined) itemData.features = (data.features || []).join(', ')
      const res = await apiPost<any>(`${API}.update_item`, { name: id, data: itemData })
      if (!res?.success) return false
      await this.fetchRooms()
      return true
    },

    async removeRoom(id?: string, force?: boolean): Promise<boolean | { hasBookings: number }> {
      if (!id) return false
      const res = await apiPost<any>(`${API}.delete_item`, { name: id, force: force ? 1 : 0 })
      if (res?.has_bookings) return { hasBookings: res.has_bookings }
      if (!res?.success) return false
      this.rooms = this.rooms.filter((r) => r.id !== id)
      return true
    },

    async addItem(data?: Partial<Item>): Promise<Item | null> {
      const itemData: Record<string, any> = {
        item_name: data?.name,
        subtitle: data?.subtitle || '',
        item_type: data?.type || 'Person',
        class: data?.class || '',
        user: data?.userId || null,
        group: data?.groupId || null,
      }
      const res = await apiPost<any>(`${API}.create_item`, { data: itemData })
      if (!res?.name) return null
      await this.fetchAdminItems()
      return { id: res.name, name: data?.name || '', subtitle: data?.subtitle || '', type: data?.type || 'Person', class: data?.class || '', slotsAvailable: 0, userId: data?.userId || '', groupId: data?.groupId }
    },

    async updateItem(id?: string, data?: Partial<Item>): Promise<boolean> {
      if (!id) return false
      const itemData: Record<string, any> = {}
      if (data?.name !== undefined) itemData.item_name = data.name
      if (data?.subtitle !== undefined) itemData.subtitle = data.subtitle
      if (data?.type !== undefined) itemData.item_type = data.type
      if (data?.class !== undefined) itemData.class = data.class
      if (data?.userId !== undefined) itemData.user = data.userId || null
      if (data?.groupId !== undefined) itemData.group = data.groupId || null
      const res = await apiPost<any>(`${API}.update_item`, { name: id, data: itemData })
      if (!res?.success) return false
      await this.fetchAdminItems()
      return true
    },

    async removeItem(id?: string, force?: boolean): Promise<boolean | { hasBookings: number }> {
      if (!id) return false
      const res = await apiPost<any>(`${API}.delete_item`, { name: id, force: force ? 1 : 0 })
      if (res?.has_bookings) return { hasBookings: res.has_bookings }
      if (!res?.success) return false
      this.items = this.items.filter((i) => i.id !== id)
      return true
    },

    async addGroup(name?: string): Promise<ItemGroup | null> {
      if (!name) return null
      const res = await apiPost<any>(`${API}.create_group`, { group_name: name })
      if (!res?.name) return null
      await this.fetchGroups()
      return { id: res.name, name }
    },

    async updateGroup(id?: string, name?: string): Promise<boolean> {
      if (!id || !name) return false
      const res = await apiPost<any>(`${API}.update_group`, { name: id, group_name: name })
      if (!res?.success) return false
      await this.fetchGroups()
      return true
    },

    async removeGroup(id?: string): Promise<boolean> {
      if (!id) return false
      const res = await apiPost<any>(`${API}.delete_group`, { name: id })
      if (!res?.success) return false
      this.groups = this.groups.filter((g) => g.id !== id)
      return true
    },

    addTimeSlot(time: string): boolean {
      if (this.timeSlots.includes(time)) return false
      this.timeSlots.push(time)
      this.timeSlots.sort()
      return true
    },

    removeTimeSlot(index: number): boolean {
      if (index < 0 || index >= this.timeSlots.length) return false
      this.timeSlots.splice(index, 1)
      return true
    },

    reorderTimeSlot(fromIndex: number, toIndex: number): boolean {
      if (fromIndex < 0 || fromIndex >= this.timeSlots.length) return false
      if (toIndex < 0 || toIndex >= this.timeSlots.length) return false
      const [item] = this.timeSlots.splice(fromIndex, 1)
      this.timeSlots.splice(toIndex, 0, item)
      return true
    },

    async addPersonBlock(itemId?: string, date?: string, start?: string, end?: string, duration?: number): Promise<number> {
      if (!itemId || !date || !start || !end || !duration) return 0
      const res = await apiPost<any>(`${API}.add_available_slots`, {
        item: itemId,
        date,
        start_time: start,
        end_time: end,
        duration,
      })
      if (!res?.success) return 0
      await this.fetchSlots(itemId, date)
      return res.created || 0
    },

    async removePersonSlot(id?: string): Promise<boolean | { hasBookings: number }> {
      if (!id) return false
      const res = await apiPost<any>(`${API}.delete_available_slot`, { name: id })
      if (res?.has_bookings) return { hasBookings: res.has_bookings }
      if (!res?.success) return false
      this.slots = this.slots.filter((s) => s.id !== id)
      return true
    },

    async bulkAddPersonSlots(itemIds?: string[], dates?: string[], start?: string, end?: string, duration?: number): Promise<number> {
      if (!itemIds || !dates || itemIds.length === 0 || dates.length === 0) return 0
      const res = await apiPost<any>(`${API}.bulk_add_available_slots`, {
        items: JSON.stringify(itemIds),
        dates: JSON.stringify(dates),
        start_time: start,
        end_time: end,
        duration,
      })
      if (!res?.success) return 0
      await this.fetchItems()
      return res.created || 0
    },
  },
})
