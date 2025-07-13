<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600 px-4">
    <div class="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">🖥️ Wake Remote</h1>
        <p class="text-gray-600">{{ isRegisterMode ? 'Crear cuenta' : 'Iniciar sesión' }}</p>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Username -->
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
            Usuario
          </label>
          <input
            id="username"
            v-model="credentials.username"
            type="text"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            placeholder="Ingresa tu usuario"
          />
        </div>

        <!-- Password -->
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
            Contraseña
          </label>
          <input
            id="password"
            v-model="credentials.password"
            type="password"
            required
            :minlength="isRegisterMode ? 6 : 1"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            placeholder="Ingresa tu contraseña"
          />
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {{ errorMessage }}
        </div>

        <!-- Success Message -->
        <div v-if="successMessage" class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
          {{ successMessage }}
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="loading || !credentials.username || !credentials.password"
          class="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span v-if="loading">{{ isRegisterMode ? 'Registrando...' : 'Iniciando sesión...' }}</span>
          <span v-else>{{ isRegisterMode ? 'Registrarse' : 'Iniciar Sesión' }}</span>
        </button>

        <!-- Toggle Mode -->
        <button
          type="button"
          @click="toggleMode"
          class="w-full text-blue-600 hover:text-blue-700 font-medium transition-colors"
        >
          {{ isRegisterMode ? '¿Ya tienes cuenta? Inicia sesión' : '¿No tienes cuenta? Regístrate' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useAuth } from '@/composables/useAuth'
import type { LoginCredentials } from '@/types'

const { login, register, loginLoading, registerLoading } = useAuth()

const isRegisterMode = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const credentials = reactive<LoginCredentials>({
  username: '',
  password: ''
})

const loading = computed(() => loginLoading.value || registerLoading.value)

const toggleMode = () => {
  isRegisterMode.value = !isRegisterMode.value
  errorMessage.value = ''
  successMessage.value = ''
}

const handleSubmit = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  try {
    if (isRegisterMode.value) {
      const success = await register(credentials)
      if (success) {
        successMessage.value = 'Usuario registrado exitosamente. Ahora puedes iniciar sesión.'
        isRegisterMode.value = false
        credentials.password = ''
      }
    } else {
      console.log('Intentando login...')
      const success = await login(credentials)
      console.log('Login result:', success)
      if (!success) {
        errorMessage.value = 'Credenciales incorrectas'
      } else {
        console.log('Login exitoso!')
      }
    }
  } catch (error: any) {
    errorMessage.value = error.message || 'Error de conexión'
  }
}
</script>