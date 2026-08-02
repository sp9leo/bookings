import { ref } from 'vue'

export class ApiError extends Error {
  status?: number
  constructor(message: string, status?: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function extractErrorMessage(json: any, status: number): string {
  if (!json) return `Request failed (${status})`
  const serverMessages = json._server_messages
  if (Array.isArray(serverMessages) && serverMessages.length) {
    for (const raw of serverMessages) {
      try {
        const parsed = typeof raw === 'string' ? JSON.parse(raw) : raw
        if (parsed?.message) return parsed.message
      } catch {
        if (typeof raw === 'string' && raw) return raw
      }
    }
  }
  if (typeof json.message === 'string') return json.message
  if (typeof json.exception === 'string') return json.exception
  return `Request failed (${status})`
}

export function unwrapMessage(json: any): any {
  if (json && typeof json === 'object' && 'message' in json) return json.message
  return json
}

export function useFetch<T = any>(
  url: string,
  params?: Record<string, any>,
  options?: { auto?: boolean; onSuccess?: (data: T) => void }
) {
  const data = ref<T | null>(null)
  const loading = ref(false)
  const error = ref<any>(null)

  async function doFetch(customParams?: Record<string, any>): Promise<T | null> {
    loading.value = true
    error.value = null
    try {
      const merged = { ...params, ...customParams }
      const query = new URLSearchParams()
      Object.entries(merged).forEach(([k, v]) => {
        if (v !== undefined && v !== null) query.append(k, String(v))
      })
      const qs = query.toString()
      const res = await fetch(url + (qs ? '?' + qs : ''))
      const json = await res.json()
      const msg = unwrapMessage(json)
      data.value = msg as T
      options?.onSuccess?.(msg as T)
      return msg as T
    } catch (e) {
      error.value = e
      return null
    } finally {
      loading.value = false
    }
  }

  if (options?.auto !== false) {
    doFetch()
  }

  return { data, loading, error, fetch: doFetch }
}

export async function apiGet<T = any>(url: string, params?: Record<string, any>): Promise<T | null> {
  try {
    const query = new URLSearchParams()
    Object.entries(params || {}).forEach(([k, v]) => {
      if (v !== undefined && v !== null) query.append(k, String(v))
    })
    const qs = query.toString()
    const res = await fetch(url + (qs ? '?' + qs : ''))
    const json = await res.json()
    return unwrapMessage(json) as T
  } catch {
    return null
  }
}

export function getCsrfToken(): string {
  const match = document.cookie.match(/(?:^|;\s*)csrf_token=([^;]*)/)
  return match ? decodeURIComponent(match[1]) : ''
}

export async function apiPost<T = any>(url: string, body: Record<string, any>): Promise<T> {
  let res: Response
  try {
    res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Frappe-CSRF-Token': getCsrfToken() },
      body: JSON.stringify(body),
    })
  } catch {
    throw new ApiError('Network error — could not reach the server')
  }

  if (!res.ok) {
    const json = await res.json().catch(() => null)
    throw new ApiError(extractErrorMessage(json, res.status), res.status)
  }

  const json = await res.json().catch(() => null)
  return unwrapMessage(json) as T
}
