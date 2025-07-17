export interface User {
  id: number
  username: string
  role: 'admin' | 'user'
  equipos_count?: number
}

export interface Equipo {
  id: number
  nombre: string
  descripcion?: string
  mac_address: string
  ip_address?: string
  estado: 'encendido' | 'apagado' | 'desconocido'
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface ApiResponse<T = any> {
  success: boolean
  message?: string
  error?: string
  data?: T
  equipos?: Equipo[]
  equipo?: Equipo
  user?: User
  token?: string
  total?: number
  user_role?: string
  users?: User[]
}

export interface CreateEquipoData {
  nombre: string
  descripcion?: string
  mac_address: string
  ip_address?: string
}

export interface UpdateEquipoData {
  nombre?: string
  descripcion?: string
  mac_address?: string
  ip_address?: string
}