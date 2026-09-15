export async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch('/api' + path, { credentials: 'include', ...options })
  if (!response.ok) {
    const data = await response.json().catch(() => ({ detail: response.statusText }))
    const detail = typeof data.detail === 'string' ? data.detail : 'Check the submitted fields and try again.'
    throw new Error(detail || 'The request could not be completed.')
  }
  return response.json()
}
export function post<T>(path: string, body: unknown = {}): Promise<T> {
  return request<T>(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
}
