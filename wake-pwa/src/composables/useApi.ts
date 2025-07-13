import axios, { type AxiosInstance, type AxiosResponse } from 'axios'
import { ref, computed } from 'vue'
import type { ApiResponse } from '@/types'

const API_BASE_URL = 'http://localhost:5000/api'

// Estado global de autenticación
const authToken = ref(localStorage.getItem('auth_token') || '')
const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

// Función global para limpiar autenticación
const clearAuthGlobal = () => {
  authToken.value = ''
  user.value = null
  localStorage.removeItem('auth_token')
  localStorage.removeItem('user')
}

// Cliente axios configurado
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

// Interceptor para agregar token
apiClient.interceptors.request.use((config) => {
  if (authToken.value) {
    config.headers.Authorization = `Bearer ${authToken.value}`
  }
  return config
})

// Interceptor para manejar errores
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearAuthGlobal()
      // No forzar navegación, dejar que Vue maneje la reactividad
    }
    return Promise.reject(error)
  }
)

export function useApi() {
  const loading = ref(false)
  const error = ref<string | null>(null)

  const setAuthToken = (token: string) => {
    authToken.value = token
    localStorage.setItem('auth_token', token)
  }

  const clearAuth = () => {
    authToken.value = ''
    user.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user')
  }

  const setUser = (userData: any) => {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const isAuthenticated = computed(() => !!authToken.value)

  async function apiCall<T>(
    method: 'get' | 'post' | 'put' | 'delete',
    url: string,
    data?: any
  ): Promise<ApiResponse<T>> {
    loading.value = true
    error.value = null

    try {
      const response: AxiosResponse<ApiResponse<T>> = await apiClient({
        method,
        url,
        data
      })
      return response.data
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.message || 'Error de conexión'
      error.value = errorMessage
      throw new Error(errorMessage)
    } finally {
      loading.value = false
    }
  }

  return {
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    isAuthenticated,
    user: computed(() => user.value),
    authToken: computed(() => authToken.value),
    setAuthToken,
    setUser,
    clearAuth,
    apiCall
  }
}