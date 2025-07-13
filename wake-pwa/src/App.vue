<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAuth } from './composables/useAuth'
import LoginForm from './components/LoginForm.vue'
import Dashboard from './components/Dashboard.vue'

const { isAuthenticated, user } = useAuth()

// Verificar autenticación al cargar
onMounted(() => {
  // La verificación se hace automáticamente en useAuth
})
</script>

<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Pantalla de login -->
    <LoginForm v-if="!isAuthenticated" />
    
    <!-- Dashboard principal -->
    <Dashboard v-else />
  </div>
</template>
