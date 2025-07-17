import { ref, computed } from 'vue'
import { useNotifications } from './useNotifications'
import { useApi } from './useApi'
import type { Equipo } from '@/types'

export const useEquipoCard = (equipo: Equipo) => {
  const { success, error } = useNotifications()
  const { post } = useApi()
  
  const waking = ref(false)
  const refreshing = ref(false)

  const statusIcon = computed(() => {
    switch (equipo.estado) {
      case 'encendido': return '🟢'
      case 'apagado': return '🔴'
      default: return '🟡'
    }
  })

  const statusText = computed(() => {
    switch (equipo.estado) {
      case 'encendido': return 'Encendido'
      case 'apagado': return 'Apagado'
      default: return 'Desconocido'
    }
  })

  const statusClasses = computed(() => {
    switch (equipo.estado) {
      case 'encendido': return 'bg-green-500'
      case 'apagado': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  })

  const handleWake = async () => {
    if (waking.value) return
    
    waking.value = true
    
    try {
      const response = await post('/wake', {
        id: equipo.id
      })

      if (response.success) {
        success(
          'Comando enviado',
          `Paquete Wake-on-LAN enviado a ${equipo.nombre}`
        )
      } else {
        error('Error', response.message || 'Error al enviar comando')
      }
    } catch (err: any) {
      error(
        'Error de conexión',
        `No se pudo enviar el comando a ${equipo.nombre}`
      )
    } finally {
      setTimeout(() => {
        waking.value = false
      }, 2000)
    }
  }

  const handleRefresh = async () => {
    if (refreshing.value) return
    
    refreshing.value = true
    
    try {
      // Simular actualización
      await new Promise(resolve => setTimeout(resolve, 1000))
      success('Estado actualizado', `Estado de ${equipo.nombre} verificado`)
    } catch (err) {
      error('Error', 'No se pudo actualizar el estado')
    } finally {
      refreshing.value = false
    }
  }

  return {
    waking,
    refreshing,
    statusIcon,
    statusText,
    statusClasses,
    handleWake,
    handleRefresh
  }
}