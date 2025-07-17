import { ref, reactive, computed } from 'vue'
import { useAuth } from './useAuth'
import { useNotifications } from './useNotifications'
import type { LoginCredentials } from '@/types'

export const useLoginForm = () => {
  const { login, register, loginLoading, registerLoading } = useAuth()
  const { success, error } = useNotifications()

  const isRegisterMode = ref(false)

  const credentials = reactive<LoginCredentials>({
    username: '',
    password: ''
  })

  const loading = computed(() => loginLoading.value || registerLoading.value)

  const toggleMode = () => {
    isRegisterMode.value = !isRegisterMode.value
    resetForm()
  }

  const resetForm = () => {
    credentials.username = ''
    credentials.password = ''
  }

  const validateForm = (): boolean => {
    if (!credentials.username.trim()) {
      error('Error de validación', 'El usuario es requerido')
      return false
    }

    if (!credentials.password) {
      error('Error de validación', 'La contraseña es requerida')
      return false
    }

    if (isRegisterMode.value && credentials.password.length < 6) {
      error('Error de validación', 'La contraseña debe tener al menos 6 caracteres')
      return false
    }

    return true
  }

  const handleSubmit = async () => {
    if (!validateForm()) return

    try {
      if (isRegisterMode.value) {
        const loginSuccess = await register(credentials)
        if (loginSuccess) {
          success(
            'Registro exitoso',
            'Usuario registrado correctamente. Ahora puedes iniciar sesión.'
          )
          isRegisterMode.value = false
          credentials.password = ''
        }
      } else {
        const loginSuccess = await login(credentials)
        if (loginSuccess) {
          success('Bienvenido', `Hola ${credentials.username}!`)
        } else {
          error('Error de autenticación', 'Credenciales incorrectas')
        }
      }
    } catch (err: any) {
      error(
        'Error de conexión',
        err.message || 'No se pudo conectar con el servidor'
      )
    }
  }

  return {
    isRegisterMode,
    credentials,
    loading,
    toggleMode,
    handleSubmit,
    resetForm
  }
}