<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <h2 class="text-2xl font-bold text-gray-900">
        🖥️ {{ user?.role === 'admin' ? 'Todos los Equipos' : 'Mis Equipos' }} ({{ equipos.length }})
      </h2>
      
      <button
        @click="refreshEquipos"
        :disabled="loading"
        class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-gray-600 to-gray-700 text-white rounded-lg hover:from-gray-700 hover:to-gray-800 disabled:opacity-50 transition-all duration-200 transform hover:scale-[1.02]"
      >
        <span class="mr-2" :class="{ 'animate-spin': loading }">🔄</span>
        {{ loading ? 'Actualizando...' : 'Actualizar Todo' }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading && equipos.length === 0" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-600">Cargando equipos...</p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="equipos.length === 0 && !loading" class="text-center py-12">
      <div class="text-6xl mb-4">🖥️</div>
      <h3 class="text-xl font-semibold text-gray-900 mb-2">No tienes equipos registrados</h3>
      <p class="text-gray-600 mb-6">Agrega tu primer equipo para comenzar a administrar tu red</p>
      <div class="inline-flex items-center px-4 py-2 bg-blue-100 text-blue-700 rounded-lg">
        💡 Usa el botón "➕ Agregar" para crear tu primer equipo
      </div>
    </div>

    <!-- Equipos Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <EquipoCard
        v-for="equipo in equipos"
        :key="equipo.id"
        :equipo="equipo"
        @wake="handleWake"
        @edit="handleEdit"
        @delete="handleDelete"
        @refresh="refreshSingleEquipo"
      />
    </div>

    <!-- Edit Modal -->
    <EditEquipoModal
      :is-open="showEditModal"
      :equipo="selectedEquipo"
      @close="closeEditModal"
      @updated="handleEquipoUpdated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useEquipos } from '@/composables/useEquipos'
import { useNotifications } from '@/composables/useNotifications'
import { useAuth } from '@/composables/useAuth'
import EquipoCard from './EquipoCard.vue'
import EditEquipoModal from './EditEquipoModal.vue'
import type { Equipo } from '@/types'

const { equipos, loading, fetchEquipos, deleteEquipo, wakeEquipo, getEquipoStatus } = useEquipos()
const { success, error, warning } = useNotifications()
const { user } = useAuth()

const showEditModal = ref(false)
const selectedEquipo = ref<Equipo | null>(null)

const refreshEquipos = async () => {
  try {
    await fetchEquipos()
    success('Lista actualizada', 'Equipos actualizados correctamente')
  } catch (err: any) {
    error('Error de conexión', err.message || 'No se pudo cargar la lista de equipos')
  }
}

const refreshSingleEquipo = async (id: number) => {
  try {
    await getEquipoStatus(id)
  } catch (err) {
    // Silenciar errores individuales para no spam de notificaciones
  }
}

const handleWake = async (equipo: Equipo) => {
  try {
    const success_wake = await wakeEquipo(equipo.id)
    if (success_wake) {
      // La notificación se maneja en useEquipoCard
      setTimeout(() => {
        refreshSingleEquipo(equipo.id)
      }, 2000)
    }
  } catch (err: any) {
    error('Error al encender', err.message || `No se pudo enviar comando a ${equipo.nombre}`)
  }
}

const handleEdit = (equipo: Equipo) => {
  selectedEquipo.value = equipo
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  selectedEquipo.value = null
}

const handleEquipoUpdated = (updatedEquipo: Equipo) => {
  // Actualizar el equipo en la lista local
  const index = equipos.value.findIndex(e => e.id === updatedEquipo.id)
  if (index !== -1) {
    equipos.value[index] = updatedEquipo
  }
}

const handleDelete = async (equipo: Equipo) => {
  // Usar notificación de advertencia en lugar de confirm
  warning(
    'Confirmar eliminación',
    `¿Estás seguro de eliminar "${equipo.nombre}"? Esta acción no se puede deshacer.`,
    { 
      persistent: true,
      duration: 10000 
    }
  )

  // Crear un confirm personalizado con setTimeout para dar tiempo a leer
  const confirmed = confirm(`¿Estás seguro de eliminar "${equipo.nombre}"?\n\nEsta acción no se puede deshacer.`)
  
  if (confirmed) {
    try {
      const success_delete = await deleteEquipo(equipo.id)
      if (success_delete) {
        success('Equipo eliminado', `${equipo.nombre} ha sido eliminado correctamente`)
      }
    } catch (err: any) {
      error('Error al eliminar', err.message || 'No se pudo eliminar el equipo')
    }
  }
}

onMounted(() => {
  refreshEquipos()
})
</script>