<template>
  <div class="max-w-2xl mx-auto">
    <div class="bg-white rounded-xl shadow-md p-8">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">➕ Agregar Nuevo Equipo</h2>
      
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Nombre del Equipo -->
        <div>
          <label for="nombre" class="block text-sm font-medium text-gray-700 mb-2">
            📛 Nombre del Equipo
          </label>
          <input
            id="nombre"
            v-model="equipoData.nombre"
            type="text"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors bg-gray-50 focus:bg-white"
            placeholder="Ej: PC-Oficina-01, Laptop-Juan, Servidor-Principal"
          />
        </div>

        <!-- Descripción -->
        <div>
          <label for="descripcion" class="block text-sm font-medium text-gray-700 mb-2">
            📝 Descripción (Opcional)
          </label>
          <input
            id="descripcion"
            v-model="equipoData.descripcion"
            type="text"
            class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors bg-gray-50 focus:bg-white"
            placeholder="Ej: Computadora de la oficina principal"
          />
        </div>

        <!-- Dirección MAC -->
        <div>
          <label for="mac" class="block text-sm font-medium text-gray-700 mb-2">
            🔗 Dirección MAC
          </label>
          <input
            id="mac"
            v-model="macInput"
            @input="handleMacInput"
            type="text"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors font-mono bg-gray-50 focus:bg-white uppercase"
            placeholder="AA:BB:CC:DD:EE:FF"
          />
          <p class="mt-1 text-sm text-gray-500">
            Formato: AA:BB:CC:DD:EE:FF (se autoformatea mientras escribes)
          </p>
        </div>

        <!-- Dirección IP -->
        <div>
          <label for="ip" class="block text-sm font-medium text-gray-700 mb-2">
            🌐 Dirección IP (Opcional)
          </label>
          <input
            id="ip"
            v-model="equipoData.ip_address"
            type="text"
            pattern="^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
            class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors font-mono bg-gray-50 focus:bg-white"
            placeholder="192.168.1.100"
          />
          <p class="mt-1 text-sm text-gray-500">
            Formato: XXX.XXX.XXX.XXX (ayuda a identificar el equipo)
          </p>
        </div>

        <!-- Submit Button -->
        <div class="flex gap-4">
          <button
            type="submit"
            :disabled="loading || !isFormValid"
            class="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-4 rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98]"
          >
            <span v-if="loading" class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Agregando...
            </span>
            <span v-else>✅ Agregar Equipo</span>
          </button>
        </div>
      </form>

      <!-- Help Section -->
      <div class="mt-8 pt-8 border-t border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">💡 ¿Cómo encontrar la dirección MAC?</h3>
        
        <div class="space-y-4">
          <div class="bg-blue-50 border-l-4 border-blue-400 p-4 rounded">
            <div class="font-semibold text-blue-900">Windows:</div>
            <code class="text-sm bg-gray-100 px-2 py-1 rounded mt-1 inline-block">ipconfig /all</code>
          </div>
          
          <div class="bg-green-50 border-l-4 border-green-400 p-4 rounded">
            <div class="font-semibold text-green-900">Linux/Mac:</div>
            <code class="text-sm bg-gray-100 px-2 py-1 rounded mt-1 inline-block mr-2">ifconfig</code>
            <span class="text-gray-600">o</span>
            <code class="text-sm bg-gray-100 px-2 py-1 rounded mt-1 inline-block ml-2">ip addr</code>
          </div>
          
          <div class="bg-purple-50 border-l-4 border-purple-400 p-4 rounded">
            <div class="font-semibold text-purple-900">Router:</div>
            <div class="text-sm text-purple-800 mt-1">
              Busca en la lista de dispositivos conectados en la interfaz web de tu router
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useEquipos } from '@/composables/useEquipos'
import { useNotifications } from '@/composables/useNotifications'
import type { CreateEquipoData } from '@/types'

interface Emits {
  equipoAdded: []
}

const emit = defineEmits<Emits>()

const { loading, createEquipo, formatMacAddress, validateMacAddress } = useEquipos()
const { success, error } = useNotifications()

const equipoData = reactive<CreateEquipoData>({
  nombre: '',
  descripcion: '',
  mac_address: '',
  ip_address: ''
})

const macInput = ref('')

const isFormValid = computed(() => {
  const hasValidName = equipoData.nombre.trim().length > 0
  const hasValidMac = equipoData.mac_address && equipoData.mac_address.trim().length >= 12
  const hasValidIp = !equipoData.ip_address || /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(equipoData.ip_address.trim())
  
  return hasValidName && hasValidMac && hasValidIp
})

const handleMacInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  // Convertir a uppercase y mantener solo caracteres válidos
  const value = target.value.toUpperCase().replace(/[^0-9A-F:-]/g, '')
  const formatted = formatMacAddress(value)
  macInput.value = formatted
  equipoData.mac_address = formatted
}

const resetForm = () => {
  equipoData.nombre = ''
  equipoData.descripcion = ''
  equipoData.mac_address = ''
  equipoData.ip_address = ''
  macInput.value = ''
}

const handleSubmit = async () => {
  if (!isFormValid.value) {
    error('Error de validación', 'Por favor completa todos los campos requeridos correctamente')
    return
  }

  if (!validateMacAddress(equipoData.mac_address)) {
    error('MAC inválida', 'El formato debe ser AA:BB:CC:DD:EE:FF')
    return
  }

  try {
    const equipoToCreate = {
      ...equipoData,
      descripcion: equipoData.descripcion?.trim() || undefined,
      ip_address: equipoData.ip_address?.trim() || undefined
    }

    const success_create = await createEquipo(equipoToCreate)
    if (success_create) {
      success(
        'Equipo agregado',
        `${equipoData.nombre} ha sido agregado exitosamente`
      )
      
      resetForm()
      emit('equipoAdded')
    }
  } catch (err: any) {
    error(
      'Error al agregar equipo',
      err.message || 'No se pudo conectar con el servidor'
    )
  }
}
</script>