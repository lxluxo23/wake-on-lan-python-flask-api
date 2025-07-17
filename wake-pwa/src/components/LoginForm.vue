<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 via-purple-600 to-indigo-700 px-4">
    <div class="max-w-md w-full">
      <!-- Animated Card -->
      <div class="bg-white/95 backdrop-blur-sm rounded-3xl shadow-2xl p-8 border border-white/20">
        <!-- Header with Animation -->
        <div class="text-center mb-8">
          <div class="inline-block p-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full mb-4">
            <span class="text-3xl">🖥️</span>
          </div>
          <h1 class="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent mb-2">
            Wake Remote
          </h1>
          <p class="text-gray-600 font-medium">
            {{ isRegisterMode ? '✨ Crear cuenta' : '🔐 Iniciar sesión' }}
          </p>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Username -->
          <div class="space-y-2">
            <label for="username" class="block text-sm font-semibold text-gray-700">
              👤 Usuario
            </label>
            <input
              id="username"
              v-model="credentials.username"
              type="text"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-gray-50 focus:bg-white"
              placeholder="Ingresa tu usuario"
            />
          </div>

          <!-- Password -->
          <div class="space-y-2">
            <label for="password" class="block text-sm font-semibold text-gray-700">
              🔒 Contraseña
            </label>
            <input
              id="password"
              v-model="credentials.password"
              type="password"
              required
              :minlength="isRegisterMode ? 6 : 1"
              class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-gray-50 focus:bg-white"
              placeholder="Ingresa tu contraseña"
            />
            <p v-if="isRegisterMode" class="text-xs text-gray-500">
              Mínimo 6 caracteres
            </p>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading || !credentials.username || !credentials.password"
            class="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-4 rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98]"
          >
            <span v-if="loading" class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isRegisterMode ? 'Registrando...' : 'Iniciando sesión...' }}
            </span>
            <span v-else>
              {{ isRegisterMode ? '✨ Registrarse' : '🚀 Iniciar Sesión' }}
            </span>
          </button>

          <!-- Toggle Mode -->
          <div class="text-center">
            <button
              type="button"
              @click="toggleMode"
              class="text-blue-600 hover:text-blue-700 font-medium transition-colors underline decoration-2 underline-offset-2 hover:decoration-blue-700"
            >
              {{ isRegisterMode ? '👋 ¿Ya tienes cuenta? Inicia sesión' : '🆕 ¿No tienes cuenta? Regístrate' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useLoginForm } from '@/composables/useLoginForm'

const {
  isRegisterMode,
  credentials,
  loading,
  toggleMode,
  handleSubmit
} = useLoginForm()
</script>