import { ref } from 'vue'
import { useApi } from './useApi'
import type { LoginCredentials, User, ApiResponse } from '@/types'

export function useAuth() {
  const { apiCall, setAuthToken, setUser, clearAuth: clearAuthLocal, isAuthenticated, user } = useApi()
  const loginLoading = ref(false)
  const registerLoading = ref(false)

  async function login(credentials: LoginCredentials): Promise<boolean> {
    loginLoading.value = true
    try {
      const response: ApiResponse = await apiCall('post', '/auth/login', credentials)
      console.log('Login response:', response)
      
      if (response.success && response.token && response.user) {
        console.log('Setting token:', response.token)
        console.log('Setting user:', response.user)
        setAuthToken(response.token)
        setUser(response.user)
        console.log('Auth state after login:', localStorage.getItem('auth_token'))
        return true
      }
      return false
    } catch (error) {
      throw error
    } finally {
      loginLoading.value = false
    }
  }

  async function register(credentials: LoginCredentials): Promise<boolean> {
    registerLoading.value = true
    try {
      const response: ApiResponse = await apiCall('post', '/auth/register', credentials)
      return response.success || false
    } catch (error) {
      throw error
    } finally {
      registerLoading.value = false
    }
  }

  async function logout(): Promise<void> {
    try {
      await apiCall('post', '/auth/logout')
    } catch (error) {
      // Ignorar errores de logout
    } finally {
      clearAuthLocal()
    }
  }

  return {
    isAuthenticated,
    user,
    loginLoading,
    registerLoading,
    login,
    register,
    logout
  }
}