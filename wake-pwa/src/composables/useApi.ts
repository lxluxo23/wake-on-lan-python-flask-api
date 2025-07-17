import axios, { type AxiosInstance, type AxiosResponse } from 'axios'
import { ref, computed } from 'vue'
import type { ApiResponse } from '@/types'
import { useConfig } from './useConfig'

const { apiConfig, log, logError } = useConfig()

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
  baseURL: apiConfig.value.baseURL,
  timeout: apiConfig.value.timeout,
})

// Interceptor para agregar token y logging
apiClient.interceptors.request.use((config) => {
  if (authToken.value) {
    config.headers.Authorization = `Bearer ${authToken.value}`
  }
  
  log('API Request:', {
    method: config.method?.toUpperCase(),
    url: config.url,
    baseURL: config.baseURL
  })
  
  return config
})

// Interceptor para manejar errores y logging
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    log('API Response:', {
      status: response.status,
      url: response.config.url,
      data: response.data
    })
    return response
  },
  (error) => {
    const errorInfo = {
      status: error.response?.status,
      url: error.config?.url,
      message: error.message,
      data: error.response?.data
    }
    
    logError('API Error:', errorInfo)
    
    if (error.response?.status === 401) {
      log('Token expirado, limpiando autenticación')
      clearAuthGlobal()
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

  // Métodos HTTP específicos para facilitar el uso
  const get = <T = any>(url: string) => apiCall<T>('get', url)
  const post = <T = any>(url: string, data?: any) => apiCall<T>('post', url, data)
  const put = <T = any>(url: string, data?: any) => apiCall<T>('put', url, data)
  const del = <T = any>(url: string) => apiCall<T>('delete', url)

  return {
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    isAuthenticated,
    user: computed(() => user.value),
    authToken: computed(() => authToken.value),
    setAuthToken,
    setUser,
    clearAuth,
    apiCall,
    // Métodos HTTP específicos
    get,
    post,
    put,
    delete: del
  }
}