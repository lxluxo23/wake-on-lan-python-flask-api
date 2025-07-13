<template>
  <div class="max-w-2xl mx-auto">
    <div class="bg-white rounded-xl shadow-md p-8">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">➕ Agregar Nuevo Equipo</h2>
      
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Nombre del Equipo -->
        <div>
          <label for="nombre" class="block text-sm font-medium text-gray-700 mb-2">
            Nombre del Equipo
          </label>
          <input
            id="nombre"
            v-model="equipoData.nombre"
            type="text"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            placeholder="Ej: PC Oficina, Laptop Juan..."
          />
        </div>

        <!-- Dirección MAC -->
        <div>
          <label for="mac" class="block text-sm font-medium text-gray-700 mb-2">
            Dirección MAC
          </label>
          <input
            id="mac"
            v-model="macInput"
            @input="handleMacInput"
            type="text"
            required
            pattern="([0-9A-F]{2}:){5}[0-9A-F]{2}"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors font-mono"
            placeholder="AA:BB:CC:DD:EE:FF"
          />
          <p class="mt-1 text-sm text-gray-500">
            Formato: AA:BB:CC:DD:EE:FF (se autoformatea mientras escribes)
          </p>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {{ errorMessage }}
        </div>

        <!-- Submit Button -->
        <div class="flex gap-4">
          <button
            type="submit"
            :disabled="loading || !isFormValid"
            class="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ loading ? 'Agregando...' : '✅ Agregar Equipo' }}
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
import type { CreateEquipoData } from '@/types'

interface Emits {
  equipoAdded: []
}

const emit = defineEmits<Emits>()

const { loading, createEquipo, formatMacAddress, validateMacAddress } = useEquipos()

const equipoData = reactive<CreateEquipoData>({
  nombre: '',
  mac_address: ''
})

const macInput = ref('')
const errorMessage = ref('')

const isFormValid = computed(() => {
  return equipoData.nombre.trim() && 
         equipoData.mac_address && 
         validateMacAddress(equipoData.mac_address)
})

const handleMacInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  const formatted = formatMacAddress(target.value)
  macInput.value = formatted
  equipoData.mac_address = formatted
}

const handleSubmit = async () => {
  errorMessage.value = ''

  if (!validateMacAddress(equipoData.mac_address)) {
    errorMessage.value = 'Formato de MAC inválido. Debe ser AA:BB:CC:DD:EE:FF'
    return
  }

  try {
    const success = await createEquipo(equipoData)
    if (success) {
      alert('Equipo agregado exitosamente!')
      
      // Reset form
      equipoData.nombre = ''
      equipoData.mac_address = ''
      macInput.value = ''
      
      // Emit event to parent
      emit('equipoAdded')
    }
  } catch (error: any) {
    errorMessage.value = error.message || 'Error al agregar equipo'
  }
}
</script>