<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <h2 class="text-2xl font-bold text-gray-900">
        Mis Equipos ({{ equipos.length }})
      </h2>
      
      <button
        @click="refreshEquipos"
        :disabled="loading"
        class="inline-flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 transition-colors"
      >
        <span class="mr-2" :class="{ 'animate-spin': loading }">🔄</span>
        {{ loading ? 'Actualizando...' : 'Actualizar' }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading && equipos.length === 0" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-600">Cargando equipos...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
      {{ errorMessage }}
    </div>

    <!-- Empty State -->
    <div v-else-if="equipos.length === 0" class="text-center py-12">
      <div class="text-6xl mb-4">🖥️</div>
      <h3 class="text-xl font-semibold text-gray-900 mb-2">No tienes equipos registrados</h3>
      <p class="text-gray-600">Agrega tu primer equipo para comenzar</p>
    </div>

    <!-- Equipos Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <EquipoCard
        v-for="equipo in equipos"
        :key="equipo.id"
        :equipo="equipo"
        @wake="handleWake"
        @delete="handleDelete"
        @refresh="refreshSingleEquipo"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useEquipos } from '@/composables/useEquipos'
import EquipoCard from './EquipoCard.vue'
import type { Equipo } from '@/types'

const { equipos, loading, fetchEquipos, deleteEquipo, wakeEquipo, getEquipoStatus } = useEquipos()

const errorMessage = ref('')

const refreshEquipos = async () => {
  try {
    errorMessage.value = ''
    await fetchEquipos()
  } catch (error: any) {
    errorMessage.value = error.message || 'Error al cargar equipos'
  }
}

const refreshSingleEquipo = async (id: number) => {
  try {
    await getEquipoStatus(id)
  } catch (error) {
    // Silenciar errores individuales
  }
}

const handleWake = async (equipo: Equipo) => {
  try {
    const success = await wakeEquipo(equipo.id)
    if (success) {
      alert(`Señal de encendido enviada a ${equipo.nombre}!`)
      // Actualizar estado después de 2 segundos
      setTimeout(() => {
        refreshSingleEquipo(equipo.id)
      }, 2000)
    }
  } catch (error: any) {
    alert(error.message || 'Error al encender equipo')
  }
}

const handleDelete = async (equipo: Equipo) => {
  if (confirm(`¿Estás seguro de eliminar "${equipo.nombre}"?`)) {
    try {
      const success = await deleteEquipo(equipo.id)
      if (success) {
        alert('Equipo eliminado exitosamente')
      }
    } catch (error: any) {
      alert(error.message || 'Error al eliminar equipo')
    }
  }
}

onMounted(() => {
  refreshEquipos()
})
</script>