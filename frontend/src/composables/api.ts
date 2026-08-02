import { ref } from 'vue'

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
      const msg = json.message ?? json
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
    return (json.message ?? json) as T
  } catch {
    return null
  }
}

export async function apiPost<T = any>(url: string, body: Record<string, any>): Promise<T | null> {
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    const json = await res.json()
    return (json.message ?? json) as T
  } catch {
    return null
  }
}
