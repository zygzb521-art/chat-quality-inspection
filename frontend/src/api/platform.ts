import request from './request'

export interface ConnectorConfig {
  id: number
  platform: string
  platform_display: string
  config_data: Record<string, string>
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface SyncLog {
  id: number
  platform: string
  platform_display: string
  status: 'running' | 'success' | 'failed'
  started_at: string
  finished_at: string | null
  conversations_pulled: number
  messages_pulled: number
  error_message: string
}

export function getConfigs() {
  return request.get<ConnectorConfig[]>('/platforms/config/')
}

export function createConfig(data: Partial<ConnectorConfig>) {
  return request.post<ConnectorConfig>('/platforms/config/', data)
}

export function updateConfig(id: number, data: Partial<ConnectorConfig>) {
  return request.put<ConnectorConfig>(`/platforms/config/${id}/`, data)
}

export function deleteConfig(id: number) {
  return request.delete(`/platforms/config/${id}/`)
}

export function getSyncLogs() {
  return request.get<SyncLog[]>('/platforms/sync-logs/')
}

export function triggerSync(data: {
  platform: string
  start_time: string
  end_time: string
}) {
  return request.post<{ task_id: string; status: string }>('/platforms/sync/', data)
}