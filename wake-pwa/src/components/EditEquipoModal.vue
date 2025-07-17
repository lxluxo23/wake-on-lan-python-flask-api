<template>
  <teleport to="body">
    <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto">
      <!-- Backdrop -->
      <div 
        class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        @click="closeModal"
      ></div>

      <!-- Modal -->
      <div class="flex min-h-full items-center justify-center p-4">
        <div 
          class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md transform transition-all"
          @click.stop
        >
          <!-- Header -->
          <div class="flex items-center justify-between p-6 border-b border-gray-200">
            <h3 class="text-xl font-semibold text-gray-900">
              ✏️ Editar Equipo
            </h3>
            <button
              @click="closeModal"
              class="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <span class="sr-only">Cerrar</span>
              ✕
            </button>
          </div>

          <!-- Form -->
          <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
            <!-- Nombre -->
            <div>
              <label for="edit-nombre" class="block text-sm font-medium text-gray-700 mb-2">
                📛 Nombre del Equipo
              </label>
              <input
                id="edit-nombre"
                v-model="formData.nombre"
                type="text"
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                placeholder="Ej: PC-Oficina-01"
              />
            </div>

            <!-- Descripción -->
            <div>
              <label for="edit-descripcion" class="block text-sm font-medium text-gray-700 mb-2">
                📝 Descripción (Opcional)
              </label>
              <input
                id="edit-descripcion"
                v-model="formData.descripcion"
                type="text"
                class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                placeholder="Ej: Computadora de la oficina principal"
              />
            </div>

            <!-- MAC Address -->
            <div>
              <label for="edit-mac" class="block text-sm font-medium text-gray-700 mb-2">
                🔗 Dirección MAC
              </label>
              <input
                id="edit-mac"
                v-model="formData.mac_address"
                @input="handleMacInput"
                type="text"
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors font-mono uppercase"
                placeholder="XX:XX:XX:XX:XX:XX"
              />
              <p class="mt-1 text-xs text-gray-500">
                Formato: XX:XX:XX:XX:XX:XX o XX-XX-XX-XX-XX-XX
              </p>
            </div>

            <!-- IP Address -->
            <div>
              <label for="edit-ip" class="block text-sm font-medium text-gray-700 mb-2">
                🌐 Dirección IP (Opcional)
              </label>
              <input
                id="edit-ip"
                v-model="formData.ip_address"
                type="text"
                pattern="^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
                class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors font-mono"
                placeholder="192.168.1.100"
              />
              <p class="mt-1 text-xs text-gray-500">
                Formato: XXX.XXX.XXX.XXX
              </p>
            </div>

            <!-- Buttons -->
            <div class="flex gap-3 pt-4">
              <button
                type="button"
                @click="closeModal"
                class="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 font-medium transition-colors"
              >
                Cancelar
              </button>
              <button
                type="submit"
                :disabled="loading || !isFormValid"
                class="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-3 rounded-xl font-medium hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <span v-if="loading" class="flex items-center justify-center">
                  <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Guardando...
                </span>
                <span v-else>💾 Guardar Cambios</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { reactive, computed, watch } from 'vue'
import { useEditEquipoModal } from '@/composables/useEditEquipoModal'
import type { Equipo } from '@/types'

interface Props {
  isOpen: boolean
  equipo: Equipo | null
}

interface Emits {
  close: []
  updated: [equipo: Equipo]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const {
  formData,
  loading,
  isFormValid,
  resetForm,
  handleSubmit: submitForm
} = useEditEquipoModal()

const closeModal = () => {
  resetForm()
  emit('close')
}

const handleMacInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  // Convertir a uppercase y mantener solo caracteres válidos
  const value = target.value.toUpperCase().replace(/[^0-9A-F:-]/g, '')
  formData.mac_address = value
}

const handleSubmit = async () => {
  const success = await submitForm()
  if (success && formData.id) {
    emit('updated', { ...formData } as Equipo)
    closeModal()
  }
}

// Watch for changes in equipo prop to populate form
watch(() => props.equipo, (newEquipo) => {
  if (newEquipo) {
    // Limpiar IP si contiene "No disponible" o valores similares
    const cleanIpAddress = (ip: string | null | undefined) => {
      if (!ip || ip === 'No disponible' || ip === 'null' || ip === 'undefined') {
        return ''
      }
      return ip
    }

    Object.assign(formData, {
      id: newEquipo.id,
      nombre: newEquipo.nombre,
      descripcion: newEquipo.descripcion || '',
      mac_address: newEquipo.mac_address.toUpperCase(),
      ip_address: cleanIpAddress(newEquipo.ip_address),
      estado: newEquipo.estado
    })
  }
}, { immediate: true })
</script>