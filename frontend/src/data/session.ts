import { computed, ref } from 'vue'

export function getSessionUserFromCookie(): string | null {
  const cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
  const user = cookies.get('user_id')
  return user === 'Guest' ? null : user
}

export const sessionUser = ref<string | null>(getSessionUserFromCookie())

export const session = {
  user: sessionUser,
  isLoggedIn: computed(() => sessionUser.value != null),
  refresh() {
    sessionUser.value = getSessionUserFromCookie()
  },
}

document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') {
    sessionUser.value = getSessionUserFromCookie()
  }
})
