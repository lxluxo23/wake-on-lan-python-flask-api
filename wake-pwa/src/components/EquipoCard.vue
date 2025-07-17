<template>
  <div class="bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-300 p-6 border border-gray-100 hover:border-blue-200">
    <!-- Header -->
    <div class="flex items-start justify-between mb-4">
      <div class="flex-1">
        <h3 class="text-lg font-semibold text-gray-900 truncate mb-1">{{ equipo.nombre }}</h3>
        <p v-if="equipo.descripcion" class="text-sm text-gray-500 truncate">{{ equipo.descripcion }}</p>
      </div>
      <div
        class="px-3 py-1 rounded-full text-sm font-medium text-white shadow-sm"
        :class="statusClasses"
      >
        {{ statusIcon }} {{ statusText }}
      </div>
    </div>

    <!-- Details -->
    <div class="space-y-3 mb-6">
      <div class="bg-gray-50 rounded-lg p-3 space-y-2">
        <div class="flex flex-col sm:flex-row sm:justify-between">
          <span class="text-sm font-medium text-gray-500">🔗 MAC:</span>
          <span class="text-sm text-gray-900 font-mono break-all">{{ equipo.mac_address }}</span>
        </div>
        <div class="flex flex-col sm:flex-row sm:justify-between">
          <span class="text-sm font-medium text-gray-500">🌐 IP:</span>
          <span class="text-sm text-gray-900 font-mono">{{ equipo.ip_address || 'No disponible' }}</span>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex flex-wrap gap-2">
      <button
        @click="handleWake"
        :disabled="waking"
        class="flex-1 min-w-[120px] bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 disabled:from-green-500 disabled:to-green-600 text-white py-2 px-4 rounded-lg font-medium transition-all duration-200 disabled:cursor-not-allowed transform hover:scale-[1.02] active:scale-[0.98]"
      >
        <span v-if="waking" class="flex items-center justify-center">
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Enviando...
        </span>
        <span v-else>⚡ Encender</span>
      </button>
      
      <button
        v-if="user?.role === 'admin'"
        @click="$emit('edit', equipo)"
        class="bg-blue-500 hover:bg-blue-600 text-white py-2 px-3 rounded-lg transition-all duration-200 transform hover:scale-[1.05] active:scale-[0.95]"
        title="Editar equipo"
      >
        ✏️
      </button>
      
      <button
        @click="handleRefresh"
        :disabled="refreshing"
        class="bg-purple-500 hover:bg-purple-600 text-white py-2 px-3 rounded-lg transition-all duration-200 transform hover:scale-[1.05] active:scale-[0.95] disabled:opacity-50"
        title="Actualizar estado"
      >
        <span v-if="refreshing">
          <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </span>
        <span v-else>🔄</span>
      </button>
      
      <button
        v-if="user?.role === 'admin'"
        @click="$emit('delete', equipo)"
        class="bg-red-500 hover:bg-red-600 text-white py-2 px-3 rounded-lg transition-all duration-200 transform hover:scale-[1.05] active:scale-[0.95]"
        title="Eliminar equipo"
      >
        🗑️
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useEquipoCard } from '@/composables/useEquipoCard'
import { useAuth } from '@/composables/useAuth'
import type { Equipo } from '@/types'

interface Props {
  equipo: Equipo
}

interface Emits {
  wake: [equipo: Equipo]
  edit: [equipo: Equipo]
  delete: [equipo: Equipo]
  refresh: [id: number]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { user } = useAuth()

const {
  waking,
  refreshing,
  statusIcon,
  statusText,
  statusClasses,
  handleWake,
  handleRefresh
} = useEquipoCard(props.equipo)
</script>