import { reactive, computed, ref } from 'vue'
import { useApi } from './useApi'
import { useNotifications } from './useNotifications'

export const useEditEquipoModal = () => {
  const { put } = useApi()
  const { success, error } = useNotifications()
  
  const loading = ref(false)

  const formData = reactive({
    id: null as number | null,
    nombre: '',
    descripcion: '',
    mac_address: '',
    ip_address: '',
    estado: 'desconocido' as 'encendido' | 'apagado' | 'desconocido'
  })

  const isFormValid = computed(() => {
    // Validación más simple y flexible
    const isNameValid = formData.nombre.trim().length > 0
    const isMacValid = formData.mac_address.trim().length >= 12 // Al menos 12 caracteres para una MAC
    const isIpValid = !formData.ip_address.trim() || /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(formData.ip_address.trim())
    
    return isNameValid && isMacValid && isIpValid
  })

  const resetForm = () => {
    formData.id = null
    formData.nombre = ''
    formData.descripcion = ''
    formData.mac_address = ''
    formData.ip_address = ''
    formData.estado = 'desconocido'
  }

  const handleSubmit = async () => {
    if (!isFormValid.value || !formData.id) {
      error('Error de validación', 'Por favor completa todos los campos requeridos correctamente')
      return false
    }

    loading.value = true

    try {
      const equipoData = {
        nombre: formData.nombre.trim(),
        descripcion: formData.descripcion.trim() || null,
        mac_address: formData.mac_address.toUpperCase().trim(),
        ip_address: formData.ip_address.trim() || null
      }

      const response = await put(`/equipos/${formData.id}`, equipoData)

      if (response.success) {
        success(
          'Equipo actualizado',
          `${formData.nombre} ha sido actualizado correctamente`
        )
        return true
      } else {
        error('Error al actualizar', response.message || 'No se pudo actualizar el equipo')
        return false
      }
    } catch (err: any) {
      error(
        'Error de conexión',
        err.message || 'No se pudo conectar con el servidor'
      )
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    formData,
    loading,
    isFormValid,
    resetForm,
    handleSubmit
  }
}