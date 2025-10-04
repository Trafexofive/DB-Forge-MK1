const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8081'
const API_TIMEOUT = parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '30000')

// For development, we'll use a default API key
// In production, this should be injected via environment variables
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || 'default-admin-key'

export interface DatabaseInstance {
  name: string // Changed from db_name to name based on backend response
  status: string
  container_id?: string
}

export interface SystemStats {
  uptime_seconds: number
  total_requests: number
  total_errors: number
  requests_by_endpoint: Record<string, number>
  errors_by_type: Record<string, number>
}

export interface QueryRequest {
  sql: string
  params?: unknown[]
}

export interface QueryResponse {
  data?: unknown[]
  rows_affected?: number
  error?: string
}

export interface CreateTableRequest {
  table_name: string
  columns: Array<{
    name: string
    type: string
    primary_key?: boolean
    not_null?: boolean
    unique?: boolean
    default?: string
  }>
}

class ApiClient {
  private baseUrl: string
  private timeout: number
  private apiKey: string

  constructor(baseUrl: string = API_BASE_URL, timeout: number = API_TIMEOUT, apiKey: string = API_KEY) {
    this.baseUrl = baseUrl
    this.timeout = timeout
    this.apiKey = apiKey
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), this.timeout)

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': this.apiKey,
          ...options.headers,
        },
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const errorText = await response.text().catch(() => 'Unknown error')
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
      }

      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        return await response.json()
      } else {
        return await response.text() as T
      }
    } catch (error) {
      clearTimeout(timeoutId)
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('Request timeout')
      }
      throw error
    }
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' })
  }

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async put<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }

  // === Database Management ===
  async getDatabases(): Promise<DatabaseInstance[]> {
    return this.get('/admin/databases')
  }

  async spawnDatabase(dbName: string) {
    return this.post(`/admin/databases/spawn/${dbName}`)
  }

  async pruneDatabase(dbName: string) {
    return this.post(`/admin/databases/prune/${dbName}`)
  }

  // === System Health & Stats ===
  async getSystemStats(): Promise<SystemStats> {
    return this.get('/admin/gateway/stats')
  }

  async getDiscovery(): Promise<Array<{ db_name: string; status: string }>> {
    return this.get('/admin/discovery')
  }

  // === Database Operations ===
  async executeQuery(dbName: string, sql: string, params?: unknown[]): Promise<QueryResponse> {
    return this.post(`/api/db/${dbName}/query`, { sql, params: params || [] })
  }

  async createTable(dbName: string, request: CreateTableRequest) {
    return this.post(`/api/db/${dbName}/tables`, request)
  }

  async insertRows(dbName: string, tableName: string, rows: Record<string, unknown>[]) {
    return this.post(`/api/db/${dbName}/tables/${tableName}/rows`, { rows })
  }

  async getRows(dbName: string, tableName: string, limit?: number, offset?: number): Promise<QueryResponse> {
    const params = new URLSearchParams()
    if (limit) params.set('limit', limit.toString())
    if (offset) params.set('offset', offset.toString())
    const query = params.toString() ? `?${params.toString()}` : ''
    return this.get(`/api/db/${dbName}/tables/${tableName}/rows${query}`)
  }

  // === Health Check (basic connectivity) ===
  async healthCheck() {
    return this.get('/')
  }
}

export const apiClient = new ApiClient()
export default apiClient