import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/book'
  },
  {
    path: '',
    component: () => import('@/layouts/PublicLayout.vue'),
    children: [
      {
        path: '/book',
        name: 'booking-home',
        component: () => import('@/pages/book/Index.vue')
      },
      {
        path: '/book/:id',
        name: 'booking-item',
        component: () => import('@/pages/book/Item.vue')
      },
      {
        path: '/book/confirm',
        name: 'booking-confirm',
        component: () => import('@/pages/book/Confirm.vue')
      },
      {
        path: '/book/my',
        name: 'my-reservations',
        component: () => import('@/pages/book/My.vue')
      },
      {
        path: '/auth/login',
        name: 'login',
        component: () => import('@/pages/auth/Login.vue')
      },
    ]
  },
  {
    path: '',
    component: () => import('@/layouts/AuthLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '/my-bookings',
        name: 'my-bookings',
        component: () => import('@/pages/rooms/MyBookings.vue')
      },
      {
        path: '/rooms',
        name: 'rooms-home',
        component: () => import('@/pages/rooms/Index.vue')
      },
      {
        path: '/rooms/schedule',
        name: 'rooms-schedule',
        component: () => import('@/pages/rooms/Schedule.vue')
      },
      {
        path: '/rooms/week-schedule',
        name: 'rooms-week-schedule',
        component: () => import('@/pages/rooms/WeekScheduleV2.vue')
      },
      {
        path: '/rooms/:id',
        name: 'rooms-book',
        component: () => import('@/pages/rooms/Book.vue')
      },
      {
        path: '/rooms/confirm',
        name: 'rooms-confirm',
        component: () => import('@/pages/rooms/Confirm.vue')
      },
      {
        path: '/rooms/my',
        name: 'rooms-my',
        component: () => import('@/pages/rooms/My.vue')
      },
      {
        path: '/admin',
        name: 'admin',
        component: () => import('@/pages/admin/Index.vue')
      },
      {
        path: '/admin/users',
        name: 'admin-users',
        component: () => import('@/pages/admin/Users.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: '/admin/rooms',
        redirect: '/admin/items?type=Room'
      },
      {
        path: '/admin/time-slots',
        name: 'admin-time-slots',
        component: () => import('@/pages/admin/TimeSlots.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: '/admin/bookings',
        name: 'admin-bookings',
        component: () => import('@/pages/admin/Bookings.vue')
      },
      {
        path: '/admin/person-slots',
        name: 'admin-person-slots',
        component: () => import('@/pages/admin/PersonSlots.vue')
      },
      {
        path: '/admin/bulk-person-slots',
        name: 'admin-bulk-person-slots',
        component: () => import('@/pages/admin/BulkPersonSlots.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: '/admin/items',
        name: 'admin-items',
        component: () => import('@/pages/admin/Items.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: '/admin/settings',
        name: 'admin-settings',
        component: () => import('@/pages/admin/Settings.vue'),
        meta: { requiresAdmin: true }
      },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  if (!authStore.isAuthenticated) {
    await authStore.init()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { path: '/auth/login', query: { redirect: to.fullPath } }
  }

  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    return { name: 'admin' }
  }

  return true
})

export default router
