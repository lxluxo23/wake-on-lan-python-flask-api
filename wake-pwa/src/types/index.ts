export interface User {
  id: number
  username: string
}

export interface Equipo {
  id: number
  nombre: string
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
}

export interface CreateEquipoData {
  nombre: string
  mac_address: string
}

export interface UpdateEquipoData {
  nombre?: string
  mac_address?: string
}