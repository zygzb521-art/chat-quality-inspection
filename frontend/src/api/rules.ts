import request from './request'

export interface Rule {
  id: number
  rule_id: string
  name: string
  description: string
  category: number
  category_name: string
  category_code: string
  rule_type: string
  config: Record<string, any>
  first_penalty: number
  second_penalty: number
  third_penalty: number
  fourth_penalty: number
  is_active: boolean
  sort_order: number
}

export interface RuleCategory {
  id: number
  name: string
  code: string
  sort_order: number
}

export function getRules() {
  return request.get<Rule[]>('/rules/')
}

export function updateRule(id: number, data: Partial<Rule>) {
  return request.put<Rule>(`/rules/${id}/`, data)
}

export function getCategories() {
  return request.get<RuleCategory[]>('/rules/categories/')
}