import request from './request'

export interface LoginData {
  username: string
  password: string
}

export interface UserInfo {
  id: number
  username: string
  email: string
  role: string
  employee_id: string
  phone: string
  first_name: string
  last_name: string
  tenant_id: number | null
}

export interface LoginResponse {
  access: string
  refresh: string
  user: UserInfo
}

export function login(data: LoginData) {
  return request.post<LoginResponse>('/auth/login/', data)
}

export function getMe() {
  return request.get<UserInfo>('/auth/me/')
}

export function refreshToken(refresh: string) {
  return request.post<{ access: string }>('/auth/refresh/', { refresh })
}