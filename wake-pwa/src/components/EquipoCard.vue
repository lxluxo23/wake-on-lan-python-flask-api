<template>
  <div class="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow p-6">
    <!-- Header -->
    <div class="flex items-start justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900 truncate">{{ equipo.nombre }}</h3>
      <div
        class="px-3 py-1 rounded-full text-sm font-medium text-white"
        :class="statusClasses"
      >
        {{ statusIcon }} {{ statusText }}
      </div>
    </div>

    <!-- Details -->
    <div class="space-y-2 mb-6">
      <div class="flex flex-col sm:flex-row sm:justify-between">
        <span class="text-sm font-medium text-gray-500">MAC:</span>
        <span class="text-sm text-gray-900 font-mono">{{ equipo.mac_address }}</span>
      </div>
      <div class="flex flex-col sm:flex-row sm:justify-between">
        <span class="text-sm font-medium text-gray-500">IP:</span>
        <span class="text-sm text-gray-900 font-mono">{{ equipo.ip_address || 'No disponible' }}</span>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex flex-col sm:flex-row gap-3">
      <button
        @click="handleWake"
        :disabled="waking"
        class="flex-1 bg-amber-500 hover:bg-amber-600 disabled:bg-green-500 text-white py-2 px-4 rounded-lg font-medium transition-colors disabled:cursor-not-allowed"
      >
        <span v-if="waking">⚡ Enviando...</span>
        <span v-else>⚡ Encender</span>
      </button>
      
      <button
        @click="$emit('refresh', equipo.id)"
        class="bg-blue-500 hover:bg-blue-600 text-white py-2 px-3 rounded-lg transition-colors"
        title="Actualizar estado"
      >
        🔄
      </button>
      
      <button
        @click="$emit('delete', equipo)"
        class="bg-red-500 hover:bg-red-600 text-white py-2 px-3 rounded-lg transition-colors"
        title="Eliminar equipo"
      >
        🗑️
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Equipo } from '@/types'

interface Props {
  equipo: Equipo
}

interface Emits {
  wake: [equipo: Equipo]
  delete: [equipo: Equipo]
  refresh: [id: number]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const waking = ref(false)

const statusIcon = computed(() => {
  switch (props.equipo.estado) {
    case 'encendido': return '🟢'
    case 'apagado': return '🔴'
    default: return '🟡'
  }
})

const statusText = computed(() => {
  switch (props.equipo.estado) {
    case 'encendido': return 'Encendido'
    case 'apagado': return 'Apagado'
    default: return 'Desconocido'
  }
})

const statusClasses = computed(() => {
  switch (props.equipo.estado) {
    case 'encendido': return 'bg-green-500'
    case 'apagado': return 'bg-red-500'
    default: return 'bg-gray-500'
  }
})

const handleWake = async () => {
  waking.value = true
  emit('wake', props.equipo)
  
  // Simular tiempo de envío
  setTimeout(() => {
    waking.value = false
  }, 2000)
}
</script>