<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <h1 class="text-2xl font-bold">🖥️ Wake Remote</h1>
          
          <div class="flex items-center space-x-4">
            <div class="text-blue-100">
              <span>Hola, {{ user?.username }}</span>
              <span v-if="user?.role" class="ml-2 px-2 py-1 bg-blue-800 rounded text-xs">
                {{ user.role === 'admin' ? '👑 Admin' : '👤 Usuario' }}
              </span>
            </div>
            
            <button
              v-if="user?.role === 'admin'"
              @click="currentView = currentView === 'add' ? 'list' : 'add'"
              class="bg-green-500 hover:bg-green-600 px-4 py-2 rounded-lg font-medium transition-colors"
            >
              {{ currentView === 'add' ? '📋 Lista' : '➕ Agregar' }}
            </button>
            
            <button
              @click="handleLogout"
              class="bg-red-500 hover:bg-red-600 px-4 py-2 rounded-lg font-medium transition-colors"
            >
              🚪 Salir
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <EquiposList v-if="currentView === 'list'" />
      <AddEquipo v-else-if="user?.role === 'admin'" @equipoAdded="currentView = 'list'" />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'
import EquiposList from './EquiposList.vue'
import AddEquipo from './AddEquipo.vue'

const { user, logout } = useAuth()
const currentView = ref<'list' | 'add'>('list')

const handleLogout = async () => {
  await logout()
}
</script>