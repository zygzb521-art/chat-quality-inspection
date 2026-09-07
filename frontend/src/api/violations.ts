import request from './request'

export interface Violation {
  id: number
  conversation: number
  rule: number
  rule_name: string
  rule_id_code: string
  employee: number | null
  employee_name: string
  platform: string
  customer_name: string
  status: string
  status_display: string
  penalty_points: number
  adjusted_penalty: number | null
  evidence_text: string
  review_notes: string
  created_at: string
}

export function getViolations(params?: Record<string, any>) {
  return request.get<Violation[]>('/violations/', { params })
}

export function getViolation(id: number) {
  return request.get<Violation>(`/violations/${id}/`)
}

export function reviewViolation(id: number, data: {
  action: 'confirm' | 'appeal' | 'close'
  adjusted_penalty?: number
  review_notes?: string
}) {
  return request.post<Violation>(`/violations/${id}/review/`, data)
}